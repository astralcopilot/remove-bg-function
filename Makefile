.PHONY: test-remote test-local

test-remote:
	@if [ -z "$(REMOTE_URL)" ]; then echo "Error: set REMOTE_URL (e.g. make test-remote REMOTE_URL=https://your-function-url)"; exit 1; fi
	@(printf '{"imageUrl": "data:image/png;base64,'; base64 -w 0 __fixtures__/img.png; printf '"}') | \
		curl -X POST $(REMOTE_URL) \
		-H "Content-Type: application/json" \
		-d @- \
		--output __fixtures__/img-no-bg-curl.png
	@echo "Result saved to __fixtures__/img-no-bg-curl.png"

test-local:
	@(printf '{"imageUrl": "data:image/png;base64,'; base64 -w 0 __fixtures__/img.png; printf '"}') | \
		curl -X POST http://localhost:8080/remove-bg \
		-H "Content-Type: application/json" \
		-d @- \
		--output __fixtures__/img-no-bg-local.png
	@echo "Result saved to __fixtures__/img-no-bg-local.png"
