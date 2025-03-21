# Flask Text-to-Speech Starter

[![Discord](https://dcbadge.vercel.app/api/server/xWRaCDBtW4?style=flat)](https://discord.gg/xWRaCDBtW4)

This example app demonstrates how to use the Deepgram Text-to-Speech API with Python using Flask, a micro web framework for Python.

<img src="/static/assets/preview-starter.png" alt="A preview of the app" style="width: 400px; height: auto; border-radius: 10px; margin-top: 20px;">

## What is Deepgram?

[Deepgram’s](https://deepgram.com/) voice AI platform provides APIs for speech-to-text, text-to-speech, and full speech-to-speech voice agents. Over 200,000+ developers use Deepgram to build voice AI products and features.

## Sign-up to Deepgram

Before you start, it's essential to generate a Deepgram API key to use in this project. [Sign-up now for Deepgram and create an API key](https://console.deepgram.com/signup?jump=keys).

## Quickstart

### Manual

Follow these steps to get started with this starter application.

#### Clone the repository

Go to GitHub and [clone the repository](https://github.com/deepgram-devs/text-to-speech-starter-python).

#### Install dependencies

Install the project dependencies.

```bash
pip install -r requirements.txt
```

#### Edit the config file

Copy the code from `sample.env` and create a new file called `.env`. Paste in the code and enter your API key you generated in the [Deepgram console](https://console.deepgram.com/).

```js
DEEPGRAM_API_KEY=%api_key%
```

#### Select branch

The `main` branch demonstrates a basic implementation, where text is sent to the API and an audio file response with synthesized text-to-speech is returned.

Checkout the other branches to see added functionality:

- [output streaming](https://github.com/deepgram-starters/text-to-speech-starter-python/tree/output-streaming): Demonstrates how to take advantage of Deepgram's output streaming feature. This example streams the audio response to the client as it is being generated.

```bash
git checkout output-streaming
```

#### Run the application

Once running, you can access the application in your browser at <http://127.0.0.1:5000>

```bash
python app.py
```

## Issue Reporting

If you have found a bug or if you have a feature request, please report them at this repository issues section. Please do not report security vulnerabilities on the public GitHub issue tracker. The [Security Policy](./SECURITY.md) details the procedure for contacting Deepgram.

## Getting Help

We love to hear from you so if you have questions, comments or find a bug in the project, let us know! You can either:

- [Open an issue in this repository](https://github.com/deepgram-starters/live-node-starter/issues/new)
- [Join the Deepgram Github Discussions Community](https://github.com/orgs/deepgram/discussions)
- [Join the Deepgram Discord Community](https://discord.gg/xWRaCDBtW4)

## Author

[Deepgram](https://deepgram.com)

## License

This project is licensed under the MIT license. See the [LICENSE](./LICENSE) file for more info.
