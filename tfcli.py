import click
import string
import requests
from secrets import choice

from tests.load.signup import new_signup
from tests.load.login import complete_login


@click.group()
def cli():
    pass


def get_rand_string(N=10):
    return "".join([choice(string.ascii_letters + string.digits) for _ in range(N)])


def generate_email():
    email = f"{get_rand_string(8)}.load@terafill.com"
    return email


from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str


BASE_URL = "http://127.0.0.1:8000/api/v1"


@click.command()
@click.option("--email", prompt="Email", help="Email of the user.")
@click.option(
    "--password", prompt="Password", hide_input=True, help="Password of the user."
)
def login_user(email, password):
    """Utility to login user."""
    login_data = complete_login(
        requests=requests,
        email=email,
        password=password,
        base_url=BASE_URL,
    )
    click.echo(login_data)


@click.command()
@click.option("--users", default=1, show_default=True, help="Number of users.")
@click.option(
    "--email",
    default=None,
    help="Email of the user. Not applicable if user count is greater than 1.",
)
@click.option("--password", default=None, help="Password of the user(s).")
def create_users(users, email, password):
    """Utility to create users."""

    if password is None or len(password) == 0:
        click.echo("Setting default password to `test`")
        password = "test"

    user_list = []

    if email is None:
        click.echo("Email(s) will be auto-generated")
        for i in range(users):
            user_list.append(User(email=generate_email(), password=password))
    elif users > 1:  # email is given
        click.echo("Warning: email parameter will be ignored")
        click.echo("Email(s) will be auto-generated")
        for i in range(users):
            user_list.append(User(email=generate_email(), password=password))
    else:  # email is given for a single user
        click.echo(f"Setting email to `{email}`")
        user_list.append(User(email=email, password=password))

    print(user_list)

    for user in user_list:
        new_signup(requests, BASE_URL, user.email, user.password)


cli.add_command(create_users)
cli.add_command(login_user)


if __name__ == "__main__":
    cli()
