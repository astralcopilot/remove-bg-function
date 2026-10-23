# Background Removal Cloud Function

Google Cloud Run function that removes backgrounds from images using [@imgly/background-removal-node](https://github.com/imgly/background-removal-js).

## Local Development

Install dependencies:

```bash
bun install
```

Start the local development server:

```bash
bun dev
```

The server will start on `http://localhost:8080`.

## Testing

### Test local version

Make sure the local server is running (`bun dev`), then:

```bash
make test-local
```

### Test deployed version

```bash
make test-remote REMOTE_URL=https://your-cloud-function-url
```

Both commands use a test image from `__fixtures__/img.png` and save the result to `__fixtures__/`.

## Models

The `models/` folder contains pre-baked ML models bundled with the function. This prevents network requests to download models at runtime, avoiding potential failures and timeouts.

## Deployment

Deploy to Google Cloud Run Functions using the [gcloud CLI](https://cloud.google.com/sdk/docs/install):

```bash
gcloud functions deploy removeBackground \
  --gen2 \
  --runtime=nodejs24 \
  --trigger-http \
  --allow-unauthenticated \
  --memory=2Gi \
  --source=.
```

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).
