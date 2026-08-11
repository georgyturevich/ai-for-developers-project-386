SPEC := tsp-output/@typespec/openapi3/openapi.yaml
DOCS := tsp-output/docs/openapi.html

.PHONY: all spec docs clean backend-install backend-run backend-test backend-lint

all: docs

spec: $(SPEC)

docs: $(DOCS)

$(SPEC): main.tsp tspconfig.yaml
	npx tsp compile .

$(DOCS): $(SPEC)
	CHROME="$$(command -v google-chrome || command -v google-chrome-stable || true)"; \
	if [ -n "$$CHROME" ]; then export PUPPETEER_EXECUTABLE_PATH="$$CHROME"; fi; \
	node_modules/.bin/redoc-cli bundle $(SPEC) -o $(DOCS) --title "Calendar Bookings API"

backend-install:
	cd backend && uv sync --all-groups

backend-run:
	cd backend && uv run uvicorn cal_bookings.app:create_app --factory --reload --port 8000

backend-test: spec
	cd backend && uv run pytest

backend-lint:
	cd backend && uv run ruff check src tests

clean:
	rm -rf tsp-output
