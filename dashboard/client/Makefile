all: style.css main.js webpack

buildDir = ./build
publicDir = ./Public

style.css: 
	sass.cmd ./src/style.scss $(buildDir)/style.css --no-source-map

webpack: 
	webpack-cli -c ./webpack.config.js 

main.js: 
	@echo "Build tsc files using tsconfig & ignore error with '-' "
	-tsc.cmd -p . 