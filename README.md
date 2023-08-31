# NC200_Camera

## Overview

Camera NC200 has dual cameras: Normal and IR.

Work of Scope:

* Read temperature

## Development

0. Install Git, Python

1. Clone the repo

    ``` cmd
    git clone https://github.com/vuquangtrong/NC200_Camera
    ```

    ``` cmd
    cd NC200_Camera
    ```

2. Create a virtual environtment

    ``` cmd
    python -m venv .venv
    ```

    Activate the environtment:

    ``` cmd
    .venv\Script\activate.bat
    ```

3. Install requirements

    ``` cmd
    pip install requests pycryptodome pymodbus
    ```

4. Activate the environtment every time starting the work on new shell/ide:

    ``` cmd
    .venv\Script\activate.bat
    ```

## Notes

* Coding convention

    Follow PEP8 rules at <https://realpython.com/python-pep8/>

* Password encryption

    NC200 uses RSA-PSS, instead of RSA-OAEP, so use `PKCS1_v1_5` cipher.
