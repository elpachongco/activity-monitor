all: style.css script.js

style.css: style.scss
	sass.cmd style.scss ../style.css --no-source-map

script.js: script.tsx
	tsc.cmd -p . --outDir ../
