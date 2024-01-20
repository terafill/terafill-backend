package utils

import (
	"fmt"

	//go get -u github.com/aws/aws-sdk-go

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ses"
)

const (
	Sender  = "harshitsaini15@gmail.com"
	Subject = "Terafill Email Verification Code"
	CharSet = "UTF-8"
)

type AWSClientPool interface {
	SendEmail(sesClient *ses.SES, input *ses.SendEmailInput) (*ses.SendEmailOutput, error)
}

type AWSClient struct{}

func (awsClient *AWSClient) SendEmail(sesClient *ses.SES, input *ses.SendEmailInput) (*ses.SendEmailOutput, error) {
	return sesClient.SendEmail(input)
}

func SetupSES() *ses.SES {
	// Create a new session in the us-west-2 region.
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("ap-south-1")},
	)

	// Create an SES session.
	sesClient := ses.New(sess)

	if err != nil {
		panic(fmt.Errorf(err.Error()))
	}

	return sesClient
}

func SendVerificationCode(awsClient AWSClientPool, sesClient *ses.SES, email string, verificationCode int) (bool, error) {
	Recipient := email
	HtmlBody := fmt.Sprintf("Your verification code is %v", verificationCode)
	TextBody := fmt.Sprintf("Your verification code is %v", verificationCode)

	// Assemble the email.
	input := &ses.SendEmailInput{
		Destination: &ses.Destination{
			CcAddresses: []*string{},
			ToAddresses: []*string{
				aws.String(Recipient),
			},
		},
		Message: &ses.Message{
			Body: &ses.Body{
				Html: &ses.Content{
					Charset: aws.String(CharSet),
					Data:    aws.String(HtmlBody),
				},
				Text: &ses.Content{
					Charset: aws.String(CharSet),
					Data:    aws.String(TextBody),
				},
			},
			Subject: &ses.Content{
				Charset: aws.String(CharSet),
				Data:    aws.String(Subject),
			},
		},
		Source: aws.String(Sender),
	}

	// Attempt to send the email.
	_, err := awsClient.SendEmail(sesClient, input)

	// Display error messages if they occur.
	if err != nil {
		if aerr, ok := err.(awserr.Error); ok {
			switch aerr.Code() {
			case ses.ErrCodeMessageRejected:
				fmt.Println(ses.ErrCodeMessageRejected, aerr.Error())
			case ses.ErrCodeMailFromDomainNotVerifiedException:
				fmt.Println(ses.ErrCodeMailFromDomainNotVerifiedException, aerr.Error())
			case ses.ErrCodeConfigurationSetDoesNotExistException:
				fmt.Println(ses.ErrCodeConfigurationSetDoesNotExistException, aerr.Error())
			default:
				fmt.Println(aerr.Error())
			}
		} else {
			// Print the error, cast err to awserr.Error to get the Code and
			// Message from an error.
			fmt.Println(err.Error())
		}

		return false, err
	}

	return true, nil
}
