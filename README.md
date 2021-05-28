## Description
This repository contains the API that exposes all the data saved in the medgold platform on the dashboard.
The code is written in `python 3.7` and is deployed on `AWS` through the `serverless framework`.

Detailed documentation on the API can be found in the docs/ folder.

## Requirements

Install node.js, npm and serverless frameworwk

### Install Node

Installation steps change based on the operating system

#### MacOS

```
brew install node
```

### Install Serverless Framework
```
npm install -g serverless
```

## Deploy

Install the dependencies

```
npm install
```

Deploy with the framework

```
sls deploy
```