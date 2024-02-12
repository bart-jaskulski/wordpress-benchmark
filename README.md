# Benchmarking WordPress with xhprof

## Results

Tested with `ddev` environment on PHP 8.1, nginx server. Profiling done with `xhprof`
extension. Benchmark was conducted against `trunk` checked out at
`b194cd1d91b1322ef405e9f0eecfbae10cef3d1e` and `autoload` checked out at
`7fa3a8f8f1877aaf7a4e5a6f286c9df445b02304`.

### Average Run Times (mean) / (median) / (stddev)
|                          | trunk | autoload | Percentage Diff |
|--------------------------|--------------|--------------|--------------|
| admin                     | 125.79ms / 121.37ms / ±22.38 | 125.02ms / 121.66ms / ±17.82 | -0.62% |
| front                     | 228.13ms / 223.95ms / ±13.45 | 230.23ms / 224.68ms / ±16.14 | 0.92% |
| rest                      | 91.55ms / 89.32ms / ±13.23 | 87.20ms / 86.25ms / ±5.17 | -4.75% |

### Average Memory Usage (mean) / (median) / (stddev)
|                          | trunk | autoload | Percentage Diff |
|--------------------------|---------|---------|---------|
| admin                     | 6.04M / 6.04M / ±0.04 | 6.23M / 6.23M / ±0.00 | 3.08% |
| front                     | 6.66M / 6.66M / ±0.00 | 6.69M / 6.69M / ±0.00 | 0.49% |
| rest                      | 5.68M / 5.68M / ±0.00 | 5.71M / 5.71M / ±0.00 | 0.5% |


## Steps to reproduce my benchmark methodology

### Clone and build WordPress repository

Test are run in the build directory, to ensure we have a fresh copy of WordPress without any development additions.

```sh
gh repo clone WordPress/wordpress-develop
cd wordpress-develop
npm install
npm run build
```

### Set up server in `build` directory

```sh
ddev config
ddev start
ddev xhprof on
```

### Run benchmarks

Benchmark is simply a sequence of 100 requests to the site for different endpoints.

```sh
for i in $(seq 1 100); do curl https://<ddev-site>/ &>/dev/null; done
for i in $(seq 1 100); do curl https://<ddev-site>/wp-json/ &>/dev/null; done
for i in $(seq 1 100); do curl -b "<authorization cookie>" https://<ddev-site>/wp-admin/ &>/dev/null; done
```

### Parse benchmarks

```sh
gh repo clone phperf/xh-tool
cd xh-tool
composer install
git apply 0001-Add-filename-to-the-output.patch
```
Finally, parse collected benchmarks and reduce it to average run times and average memory usage.

```sh
fd . ./profile/ -x xh-tool info {} --with-mem | python3 ./parse_profile.py
```