all: style.css main.js 

publicDir = ./Public

style.css: 
	sass ./src/style.scss $(publicDir)/style.css --no-source-map

main.js: 
	@echo "Build all ts* files using tsconfig & ignore error with '-' "
	-tsc -p . 