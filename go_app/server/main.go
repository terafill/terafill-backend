package main

import "github.com/gofiber/fiber/v2"

func main() {
    app := fiber.New()

    app.Get("/", func(c *fiber.Ctx) error {
        // return c.SendString("Hello, World 👋!")
        return c.SendString("{\"msg\":\"Hello this is a test message\"}")
    })

    app.Listen(":3000")
}
