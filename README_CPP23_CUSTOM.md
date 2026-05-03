# VNOJ Judge C++23 Custom Image

This branch packages the ORE/VNOJ judge image used by `ojkhanhhoa.site`.

## What is customized

- Keeps the custom invocation protocol used by the web custom input/output feature.
- Adds a `CPP23` executor.
- Updates `CPPICPC` from `gnu++20` to `gnu++23`.
- Uses GCC/G++ 15 (`g++ 15.2.0` on the deployed image), which supports C++23 mode.
- Sets the default judge compiler timeout to 30 seconds. This avoids false
  compile-timeout verdicts from modern GCC 15 C++20/C++23 builds under the DMOJ
  compiler sandbox; it does not change problem execution time limits.
- Precompiles `bits/stdc++.h` for `gnu++23` in addition to the older C++ modes.
- Builds the full image from this repository instead of downloading `master` during Docker build, so the image is reproducible from this source tree.

## Fast overlay build

Use this when `vnoj/judge-tiervnoj:latest` is already the previous custom judge base. The overlay copies the custom invocation patch files and C++23 executors into the final image:

```bash
docker build -t vnoj/judge-tiervnoj:cpp23-custom -f .docker/tiervnoj/Dockerfile.overlay .
```

## Full source build

Use this on a fresh judge machine. This is the recommended path when you do
not want to depend on `vnoj/judge-tiervnoj:latest`; the Dockerfile copies this
repository into the image and builds from the checked-out source tree.

```bash
docker build -t vnoj/judge-tiervnoj:cpp23-custom -f .docker/tiervnoj/Dockerfile .
```

The image tag still starts with `vnoj/` only for compatibility with existing
run scripts. If built with the command above, the image contents come from this
repository.

## Fresh VPS notes

A clean CentOS Stream 10 VPS may not have Docker or Git installed. Docker does
not always publish native CentOS 10 packages, so installing the EL9 Docker CE
packages worked on the current judge VPS:

```bash
dnf -y install git dnf-plugins-core curl ca-certificates
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf --releasever=9 -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker --version
```

Then clone and build:

```bash
git clone https://github.com/maithedung79/judge-tiervnoj-cpp23.git
cd judge-tiervnoj-cpp23
docker build -t vnoj/judge-tiervnoj:cpp23-custom -f .docker/tiervnoj/Dockerfile .
```

## Remote bridge access

Remote judges must be able to reach the web bridge port, usually `9999`.
On the web VPS, allow the judge VPS IP before starting the remote containers:

```bash
ufw allow from <judge-vps-ip> to any port 9999 proto tcp comment 'remote judges'
```

From the judge VPS, verify the bridge is reachable:

```bash
timeout 5 bash -lc 'cat < /dev/null > /dev/tcp/<web-vps-ip>/9999' && echo OK || echo FAIL
```

## Run judges

Same-machine example:

```bash
docker run -d --name judge01 --restart=always --network host   -v /root/site/problems:/problems   vnoj/judge-tiervnoj:cpp23-custom   run -p 9999 -c /problems/judge01.yml localhost -A 0.0.0.0 -a 9111
```

Repeat with `judge02.yml`, `judge03.yml`, and `judge04.yml` as needed.

Remote judge VPS example for `judge05`, `judge06`, and `judge07`:

```bash
for n in 05 06 07; do
  port=$((9110 + 10#$n))
  docker run -d --name judge$n --restart=always --network host \
    -v /root/problems:/problems \
    vnoj/judge-tiervnoj:cpp23-custom \
    run -p 9999 -c /problems/judge$n.yml <web-vps-ip> -A 0.0.0.0 -a $port
done
```

The `judgeXX.yml` files must already exist in the mounted problem directory and
their IDs/keys must match the judges configured in the web database.

Recommended judge config shape:

```yaml
id: judge05
key: <judge-key-from-web>
problem_storage_globs:
  - /problems/*
compiler_time_limit: 30
```

Keep `compiler_time_limit` at 30 seconds for this GCC 15 image. Lower values
can produce random CE verdicts on ordinary C++20/C++23 submissions during
rejudge bursts.

## Problem data sync

Remote judge machines need the same problem data as the web VPS. One simple
setup is to rsync the web problem directory to the judge VPS:

```bash
rsync -az --delete /root/site/problems/ root@<judge-vps-ip>:/root/problems/
```

For ongoing sync, install a cron job on the web VPS. This keeps new or edited
problems available to remote judges after the next sync interval:

```cron
*/5 * * * * root flock -n /var/lock/problem-sync-vps2.lock rsync -az --delete --timeout=30 -e "ssh -i /root/.ssh/vps2_judge_sync -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o ServerAliveInterval=5 -o ServerAliveCountMax=1" /root/site/problems/ root@<judge-vps-ip>:/root/problems/ >> /root/problem-rsync-cron.log 2>&1
```

If the judge VPS was powered off while problems were added, wait for this sync
to finish after boot before expecting the remote judges to grade those new
problems.

## Verify

Useful checks after starting containers:

```bash
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}'
docker logs --tail 80 judge05
docker run --rm --entrypoint /bin/bash vnoj/judge-tiervnoj:cpp23-custom -lc \
  'g++ --version | head -1; test -f /judge/dmoj/executors/CPP23.py && echo CPP23-file-ok; grep -q custom-invocation-request /judge/dmoj/packet.py && echo custom-packet-ok'
```

## Package image

```bash
docker save vnoj/judge-tiervnoj:cpp23-custom | gzip -1 > judge-tiervnoj-cpp23-custom.tar.gz
```
