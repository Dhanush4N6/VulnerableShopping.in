# VulnerableShopping.in

**VulnerableShopping.in** is a deliberately vulnerable e-commerce web
application created for learning and practicing web application
penetration testing in a controlled environment. It simulates common
security weaknesses in shopping websites so learners can explore how
vulnerabilities occur, test them, and understand their potential impact.

## Getting Started

Clone the repository into a folder named `vshop`, enter the project
directory, and run the startup script:

``` bash
git clone https://github.com/Dhanush4N6/VulnerableShopping.in.git vshop
cd vshop
./setup.sh
pip install -r requirement.txt
./run.sh
```

Follow any instructions displayed by the startup script. If the script
is not executable, run `chmod +x run.sh` and then `./run.sh`.

## About the Project

The application provides e-commerce-style functionality such as user
authentication, product browsing and search, shopping carts, orders,
user profiles, product reviews, and administrative features. It is
intentionally designed with security flaws to help learners understand
how insufficient input validation, weak authorization checks, and
insecure handling of user-controlled data can put an application at
risk.

Use this project only on a system you own or have explicit permission to
test. Keep it isolated from public networks and never use real
credentials or personal information.

## Attacks and Vulnerabilities You Can Learn

-   **SQL Injection (SQLi):** Learn how unsafe database queries can
    allow input to change a query's logic or expose data.
-   **Cross-Site Scripting (XSS):** Understand how untrusted input
    rendered as page content can cause script execution in a browser.
    Covers reflected and stored XSS.
-   **Insecure Direct Object Reference (IDOR):** Test whether changing
    an object identifier can expose another user's order or data when
    ownership is not checked.
-   **Cross-Site Request Forgery (CSRF):** Learn how a browser's
    authenticated session can be abused to submit an unwanted action
    when protections are missing.
-   **Server-Side Request Forgery (SSRF):** Explore how a server that
    fetches user-supplied URLs may be tricked into requesting internal
    resources.
-   **Command Injection:** Understand the risk of passing untrusted
    input to operating-system commands.
-   **Broken Access Control:** Check whether users can access
    administrative functions or resources beyond their permissions.
-   **Unrestricted File Upload:** Learn why uploaded files need strict
    type validation, safe storage, and execution controls.
-   **Open Redirect:** See how unvalidated redirect destinations can
    send users to an untrusted website.
-   **Sensitive Data Exposure:** Examine the impact of endpoints that
    reveal passwords, tokens, or other private information.
-   **Weak Authentication and Brute-Force Protection:** Assess the risk
    of missing rate limits, throttling, or account lockout controls.
-   **Business Logic and Price Manipulation:** Test whether the server
    trusts prices or other important values supplied by the client.
-   **Verbose Error Disclosure:** Understand how detailed errors can
    reveal implementation details useful to an attacker.
-   **Hardcoded Secrets:** Learn why secret keys and credentials should
    not be stored directly in application source code.

## Suggested Learning Workflow

1.  Set up the application in an isolated lab.
2.  Explore the website normally and map its available features.
3.  Test requests and parameters using browser developer tools and an
    intercepting proxy.
4.  Validate each finding safely and record the evidence.
5.  Document the impact and recommend mitigations, such as parameterized
    queries, output encoding, server-side authorization checks, CSRF
    tokens, strict URL and upload validation, rate limiting, and secure
    secret management.

## Disclaimer

This project is intended for education and authorized security testing
only. Do not test these techniques against systems without explicit
permission.

## Project Documentation
https://medium.com/@dhanush.nayaka/vulnerable-shopping-f4d741a08b5a?sharedUserId=dhanush.nayaka

