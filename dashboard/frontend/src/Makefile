all: style.css main.js bundle

outDir = ../build

style.css: 
	sass.cmd style.scss $(outDir)/style.css --no-source-map

bundle:
	@echo "overwrite main with bundled modules"
	rollup.cmd $(outDir)/main.js -o $(outDir)/main.js -f iife

main.js: 
	@echo "Build tsc files using tsconfig & ignore error with '-' "
	-tsc.cmd -p . 