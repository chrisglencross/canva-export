# Canva Presentation Exporter

## Overview

Downloads a Canva presentation as a video in a format suitable for displaying on unattended digital signage.

The `canva_export.py` script is expected to be run as an unattended cronjob on the kiosk machine, for example
a Raspberry Pi. It will export and download the presentation as a `.mp4` video file using Canva REST APIs.

The export and download will only be performed if the Canva presentation has been modified since the video was
last downloaded.

If network connectivity becomes unavailable the download will fail, but the kiosk will continue to display the
previously downloaded version of the video.

## Usage

### Configuring Authentication

The application uses OAuth credentials to authenticate to the Canva API. You will need to create a Canva Integration
following the [instructions from Canva](https://www.canva.dev/docs/connect/creating-integrations/).

* When you are given a `Client ID` and `Client secret` value, put these in a `.env` file. See `dot.env.template` as
and example. Alternatively, just copy the example `.env` file displayed on the Canva web page.
* When setting scopes, integration requires *Read* `design:content` and `design:meta` access only.
* When setting the `Authorized redirects` use `http://127.0.0.1:3001/redirect` as the only redirect.
* There is no need to enable `Return navigation`
* There is no need to `Submit for review` if you are not releasing your integration for others to use.

The first time you run the application a browser window will be displayed asking you to login to Canva and
authorize this application to use your credentials.

OAuth tokens will be cached in a file `.session.yaml` so you will only see this interactive prompt the first time
you run this application or if those cached credentials expire.

The cached credentials will be refreshed every time you run the application, and as long as you run the application
regularly, for example once a week, they should not expire.

### Command-line usage

#### Show usage instructions
```shell
$ python -m canva_export --help                            
usage: python -m canva_export [-h] -d DESIGN_ID [-o OUTPUT]

Exports presentations from Canva

options:
-h, --help            show this help message and exit
-d, --design-id DESIGN_ID
                      Canva design id
-o, --output OUTPUT   Target file
```

#### Exporting a Canva design as a video
```shell
$ python -m canva_export --design-id DAHBkoYWz0Y --output mypresentation.mp4
2026-02-20 19:52:33,837 INFO [canva_export] Downloading design modified at 2026-02-20T14:52:44+00:00
2026-02-20 19:52:33,838 INFO [canva_api] Exporting design DAHBkoYWz0Y...
2026-02-20 19:52:34,582 INFO [canva_api] Waiting for job 8b3768bf-ba55-4f72-9bf3-19e5648e585e...
2026-02-20 19:52:44,888 INFO [canva_api] Downloading to mypresentation.mp4...
2026-02-20 19:52:47,086 INFO [canva_export] Downloaded mypresentation.mp4                  
```

As well as downloading the presentation, this will write a file `mypresentation.mp4.ts` which contains only
the timestamp of when the design was last modified in Canva.

If you run the command again and the design last modified time has not changed, nothing will be downloaded:
```shell
$ python -m canva_export --design-id DAHBkoYWz0Y --output mypresentation.mp4
2026-02-20 19:57:13,588 INFO [canva_export] Design not modified since 2026-02-20T14:52:44+00:00
```

