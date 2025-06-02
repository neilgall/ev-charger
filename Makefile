FUNCTION_ARN := arn:aws:lambda:eu-west-1:188024963716:function:andersen-ev
ZIP := build/lambda_function.zip
PKG := build/packages.zip
SRC := $(shell ls *.py | grep -v ^test_)

.PHONY: all
all: $(ZIP) upload

.PHONY: clean
clean:
	rm -rf build package

build:
	mkdir -p build

requirements.txt: requirements.in
	pip-compile --output-file=$@ $^

package: requirements.txt
	mkdir -p package
	pip install -r requirements.txt --target ./package

$(PKG): build package
	rm -f $@
	(cd package && zip -r ../$(PKG) .)

$(ZIP): build $(SRC) $(PKG)
	cp -f $(PKG) $@
	zip -r $@ $(SRC)

upload: $(ZIP)
	aws lambda update-function-code \
		--function-name $(FUNCTION_ARN) \
		--zip-file fileb://$^ \
	| cat

