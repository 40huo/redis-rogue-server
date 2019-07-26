# Redis Rogue Server

A exploit for Redis 4.x RCE, inspired by [Redis post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf).

经测试Redis 5.0.5也可以使用，没有出现ppt上写的5.0无法set/get config的情况.

## Usage:

Compile .so from <https://github.com/n0b0dyCN/RedisModules-ExecuteCommand>.

去除了在内网SSRF环境下没什么用的自动化利用部分，需要手动执行slaveof等命令。
