package utils

import (
	"fmt"
	"math/rand"
	"testing"

	"github.com/aws/aws-sdk-go/service/ses"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// PrinterMock is a mock object. This object mocks the Printer interface.
type AWSClientMock struct {
	mock.Mock
}

func (d *AWSClientMock) SendEmail(sesClient *ses.SES, input *ses.SendEmailInput) (*ses.SendEmailOutput, error) {
	// indicates that the function is called
	// args := d.Called(input)

	fmt.Println("Sending mail from mock object...")
	// return &ses.SendEmailOutput{}, args.Error(0)
	return &ses.SendEmailOutput{}, nil
}

func TestSendVerificationCode(t *testing.T) {
	var sesClient *ses.SES
	var awsClient *AWSClientMock
	email := "harshitsaini15@gmail.com"

	verificationCode := rand.Intn(900000) + 100000

	res, err := SendVerificationCode(awsClient, sesClient, email, verificationCode)

	assert.NoError(t, err)
	assert.Equal(t, true, res)
}
