from dmoj.executors.c_like_executor import CPPExecutor, GCCMixin


class Executor(GCCMixin, CPPExecutor):
    command = 'g++23'
    command_paths = ['g++-15', 'g++']
    std = 'gnu++23'
    test_program = """
#include <expected>
#include <iostream>

#if __cplusplus >= 202302L
int main() {
    std::expected<int, int> value = 23;
    if (!value || value.value() != 23) {
        return 1;
    }
    auto input = std::cin.rdbuf();
    std::cout << input;
    return 0;
}
#endif
"""
