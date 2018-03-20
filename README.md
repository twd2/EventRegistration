# event-registration

[![docker image](https://images.microbadger.com/badges/image/mfmfmf/env.svg)](https://microbadger.com/images/mfmfmf/env)

A simple event-registration system.

## Prerequisites

* Linux 4.0+ (Ubuntu 16.04 LTS is recommended)
* Docker CE

## Building Docker Image

If you don't like to use the prebuilt image `mfmfmf/env` hosted on Docker Hub:

1. Run `docker build --network=host .`

## Building

1. Install [Docker CE](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
2. Run `docker pull mfmfmf/env`
3. Clone this project.
4. Run `./run_in_docker.sh build.sh`

## Development

1. Run `./run_in_docker.sh start.sh <arguments>` (if you have `secret.sh`, run `./run_in_docker.sh secret.sh` instead)
2. Browse `http://127.0.0.1:8888`

Arguments:

- `--oauth-id=`: OAuth ID
- `--oauth-secret=`: OAuth Secret
- `--listen=`: what address the web server listens. Default is `http://0.0.0.0:8888`.
- `--url-prefix=`: prefix of the website, starting with `https://` or `http://`, ending without `/`.
- `--smtp-host=`: mail server address.
- `--smtp-user=`: smtp username.
- `--smtp-password=`: corresponding password.
- `--mail-from=`: should be same as `smtp-user`.

**As an intuitive example, you may want to add a super administrator to start:**

```bash
./run_in_docker.sh set_root.sh username
```

## Deployment

Same as development.

You may use [Nginx](https://nginx.org/) reverse proxy to improve performance.

## Notes

Happy coding!

Maximum line width: 100

Indentation: 2 spaces

[JavaScript Style Guide](https://github.com/airbnb/javascript)

For design details, please see `docs/*`.

## References

* [aiohttp](http://aiohttp.readthedocs.org/en/stable/)
* [Jinja2 Documentation](http://jinja.pocoo.org/docs/)
* [Motor: Asynchronous Python driver for MongoDB](http://motor.readthedocs.org/en/stable/)
* [Webpack Module Bundler](https://webpack.js.org/)
* [Vijos UI Framework](https://github.com/vijos/vj4/tree/master/vj4/ui)
