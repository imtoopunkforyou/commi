.PHONY: strict lint fix typecheck build

strict:
	npm run check:strict

lint:
	npm run lint:strict

fix:
	npm run lint:fix

typecheck:
	npm run typecheck

build:
	npm run build
