# Clospot cafe for lambda

This is a LINE bot that can search for nearby cafes based on location information.

## Requirement

- Python:3.6
- Pipenv:2018.11.26 or later

## Install

Setup AWS:

ref(Japanese only)
- [Lambdaでline-bot-sdk-pythonを使用してオウム返しBOTを作成する](https://qiita.com/konikoni428/items/fd1ab5993bc5526726bb)

Clone repository:

```console
$ git clone https://github.com/PiroHiroPiro/clospot_cafe_lambda.git
$ cd clospot_cafe_lambda
```

Install libraries:

```console
$ pipenv install
$ pipenv shell
```

Copy configuration file:

```console
$ cp lambda.json.example ./src/lambda.json
```

Enter the Lambda function name, roles, environment variables, etc. in the copied configuration file `lambda.json`:

Upload to Lambda:

```console
$ cd src
$ lambda-uploader
```

## Licence

This software is released under the MIT License, see [LICENSE](https://github.com/PiroHiroPiro/clospot_cafe_lambda/blob/master/LICENSE).

## Author

[Hiroyuki Nishizawa](https://github.com/PiroHiroPiro)
