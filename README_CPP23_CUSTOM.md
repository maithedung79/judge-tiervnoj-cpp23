# VNOJ Judge C++23 Custom Image

This branch packages the ORE/VNOJ judge image used by `ojkhanhhoa.site`.

## What is customized

- Keeps the custom invocation protocol used by the web custom input/output feature.
- Adds a `CPP23` executor.
- Updates `CPPICPC` from `gnu++20` to `gnu++23`.
- Uses GCC/G++ 15 (`g++ 15.2.0` on the deployed image), which supports C++23 mode.
- Builds the full image from this repository instead of downloading `master` during Docker build, so the image is reproducible from this source tree.

## Fast overlay build

Use this when `vnoj/judge-tiervnoj:latest` is already the previous custom judge base. The overlay copies the custom invocation patch files and C++23 executors into the final image:

```bash
docker build -t vnoj/judge-tiervnoj:cpp23-custom -f .docker/tiervnoj/Dockerfile.overlay .
```

## Full source build

Use this on a fresh machine when the base runtime image is available:

```bash
docker build -t vnoj/judge-tiervnoj:cpp23-custom -f .docker/tiervnoj/Dockerfile .
```

## Run judges

```bash
docker run -d --name judge01 --restart=always --network host   -v /root/site/problems:/problems   vnoj/judge-tiervnoj:cpp23-custom   run -p 9999 -c /problems/judge01.yml localhost -A 0.0.0.0 -a 9111
```

Repeat with `judge02.yml`, `judge03.yml`, and `judge04.yml` as needed.

## Package image

```bash
docker save vnoj/judge-tiervnoj:cpp23-custom | gzip -1 > judge-tiervnoj-cpp23-custom.tar.gz
```
