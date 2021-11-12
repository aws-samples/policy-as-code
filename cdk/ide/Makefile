ZIPFILE ?= policy-as-code-workshop-stack-app.zip
#S3_ASSET_BUCKET ?= ee-assets-prod-us-east-1
#S3_ASSET_PREFIX ?= modules/90b84d433ffe415d829cfb33ded5c260/v1/
S3_ASSET_BUCKET ?= ee-assets-jaknn-sandbox
S3_ASSET_PREFIX ?= modules/local_testing/v1/
S3_URL := s3://$(S3_ASSET_BUCKET)/$(S3_ASSET_PREFIX)$(ZIPFILE)

.PHONY: upload
upload: $(ZIPFILE)
	@echo Note: If this fails, ensure the proper AWS credentials are set in the environment. These can be found in the Event Engine module configuration.
	aws s3 cp $(ZIPFILE) $(S3_URL)

zip: $(ZIPFILE)

$(ZIPFILE): $(shell git ls-files)
	rm -f $@
	cd ../.. && git ls-files | xargs zip cdk/ide/$@

.PHONY: clean
clean:
	rm -f $(ZIPFILE)
	find . -name '*.js' ! -name 'jest.config.js' -not -path './node_modules/*' -delete
	find . -name '*.d.ts' -not -path './node_modules/*' -delete
	rm -rf cdk.out/

.PHONY: build
build:
	npm run build

.PHONY: synth-bootstrap
synth-bootstrap: build
	npx cdk synth IdeStack

.PHONY: deploy
deploy: build upload
	npx cdk deploy IdeStack --require-approval=never \
		--previous-parameters=false \
		--parameters IdeStack:EEAssetsBucket=$(S3_ASSET_BUCKET) \
		--parameters IdeStack:EEAssetsKeyPrefix=$(S3_ASSET_PREFIX) \
		--parameters IdeStack:SourceZipFile=$(ZIPFILE) \
		--parameters IdeStack:SourceZipFileChecksum=$$(openssl sha256 -hex -r $(ZIPFILE) | cut -d' ' -f1)

.PHONY: destroy
destroy:
	npx cdk destroy IdeStack --force