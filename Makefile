SPEC := tsp-output/@typespec/openapi3/openapi.yaml
DOCS := tsp-output/docs/openapi.html

.PHONY: all spec docs clean

all: docs

spec: $(SPEC)

docs: $(DOCS)

$(SPEC): main.tsp tspconfig.yaml
	npx tsp compile .

$(DOCS): $(SPEC)
	CHROME="$$(command -v google-chrome || command -v google-chrome-stable || true)"; \
	if [ -n "$$CHROME" ]; then export PUPPETEER_EXECUTABLE_PATH="$$CHROME"; fi; \
	node_modules/.bin/redoc-cli bundle $(SPEC) -o $(DOCS) --title "Calendar Bookings API"

clean:
	rm -rf tsp-output
