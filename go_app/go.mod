module terafill.com/m

go 1.21

toolchain go1.21.5

require (
	github.com/1Password/srp v0.2.1-0.20230719120150-2d0a5a599a7c
	github.com/aws/aws-sdk-go v1.49.9
	github.com/go-sql-driver/mysql v1.7.1
	github.com/gofiber/fiber/v2 v2.51.0
	github.com/google/uuid v1.4.0
	github.com/stretchr/testify v1.8.4
)

require (
	github.com/andybalholm/brotli v1.0.5 // indirect
	github.com/davecgh/go-spew v1.1.1 // indirect
	github.com/jmespath/go-jmespath v0.4.0 // indirect
	github.com/klauspost/compress v1.16.7 // indirect
	github.com/kong/go-srp v0.0.0-20191210190804-cde1efa3c083 // indirect
	github.com/kr/pretty v0.3.1 // indirect
	github.com/mattn/go-colorable v0.1.13 // indirect
	github.com/mattn/go-isatty v0.0.20 // indirect
	github.com/mattn/go-runewidth v0.0.15 // indirect
	github.com/pmezard/go-difflib v1.0.0 // indirect
	github.com/rivo/uniseg v0.2.0 // indirect
	github.com/rogpeppe/go-internal v1.11.0 // indirect
	github.com/stretchr/objx v0.5.0 // indirect
	github.com/valyala/bytebufferpool v1.0.0 // indirect
	github.com/valyala/fasthttp v1.50.0 // indirect
	github.com/valyala/tcplisten v1.0.0 // indirect
	github.com/wault-pw/srp6ago v0.0.0-20220316105709-be5968598c33 // indirect
	golang.org/x/crypto v0.7.0 // indirect
	golang.org/x/sys v0.16.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	gopkg.in/check.v1 v1.0.0-20180628173108-788fd7840127 // indirect
	gopkg.in/square/go-jose.v2 v2.6.0 // indirect
	gopkg.in/yaml.v2 v2.4.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)

replace github.com/1Password/srp v0.2.1-0.20230719120150-2d0a5a599a7c => ../../srp
