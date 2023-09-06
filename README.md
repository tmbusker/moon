# Busking

Tools, data and programs used in daily work.

This project is based on following technologies:

- Django(v4.1.4)
- Postgres(v15)
- MkDocs(v1.4.2)

## Create a django based web application

1. Create a new python virtual environment and activate it

    ```bat title="Create a new python virtual environment"
    cd silos
    python -m venv venv
    ```

    ```bat title="activate.bat"
    echo off

    set base_path=%~d0\silos
    set venv_path=%base_path%\venv

    if "%VIRTUAL_ENV%" EQU "" (
        %venv_path%\Scripts\Activate
    )
    ```

2. Install django and other useful packages

    ```bat title="List Python packages"
    pip list
    pip install django
    pip install wheel
    pip install pylint
    pip list
    ```

3. Create a new django project

    ```bat title="Create a new Django Project"
    cd silos
    mkdir busking
    django-admin startproject busking .
    ```

    1. migrate database
        - The default database at this point is the sqllite3.

        ```bat title="Migrate database"
        python manage.py migrate
        ```

    2. create superuser

        ```bat title="create_django_super_user.bat"
        echo off
        call activate
        set DJANGO_SUPERUSER_PASSWORD=secret_word
        set DJANGO_SUPERUSER_EMAIL=someone@gmail.com

        python manage.py createsuperuser --no-input --username admin
        ```

    3. run server

        ```bat title="create_django_super_user.bat"
        echo off
        call activate

        @REM django-admin runserver [addrport]
        @REM python manage.py runserver --noreload
        python manage.py runserver
        ```

    4. confirm the application is running
        - [http://127.0.0.1:8000/](http://127.0.0.1:8000/){: target="_blank" .external }

## Documentation

Build project documentation using [MkDocs](https://www.mkdocs.org/){: target="_blank" .external }.

MkDocs uses the Python-Markdown library to render Markdown documents to HTML.

1. Install MkDocs

    ```bat title="Install MkDocs"
    pip install mkdocs
    pip install mkdocs[i18n]
    ```

2. Add MkDocs to the application

    ```bat title="Create Mkdocs Project"
    cd silos\busking
    mkdocs new .
    ```

3. Start the MkDocs server

    ```bat title="Start Mkdocs Server"
    cd busking
    mkdocs serve
    ```

4. [Access the local MkDocs site](http://127.0.0.1:8000/){: target="_blank" .external }
5. Host documents on GitHub's project pages

    ```bat title="Host Docs at GitHub"
    mkdocs gh-deploy
    ```

6. [Access the documentation site](https://tmbusker.github.io/busking/){: target="_blank" .external }
7. [MkDocs Theme](https://www.mkdocs.org/user-guide/choosing-your-theme/#using-the-theme-custom_dir){: target="_blank" .external }

    MkDocs includes two built-in themes (mkdocs and readthedocs). The default theme(mkdocs), which was built as a custom Bootstrap theme, supports most every feature of MkDocs.

8. [Python Markdown](https://python-markdown.github.io/){: target="_blank" .external }
    - Installation

    ```bat title="Install Python Markdown"
    pip install markdown
    ```

    - [Extensions](https://python-markdown.github.io/extensions/){: target="_blank" .external }

        Python Markdown offers a flexible extension mechanism, which makes it possible to change and/or extend the behavior of the parser without having to edit the actual source files.

9. [Material Theme for MkDocs](https://squidfunk.github.io/mkdocs-material/){: target="_blank" .external }
    1. Installation

        ```bat title="Install MkDoc Material Theme"
        pip install mkdocs-material
        ```

    2. Recommended configuration validation and auto-complete
        - Install Visual Studio Code extension `vscode-yaml` for YAML language support
        - Add the schema under the yaml.schemas key in your user or workspace settings.json:

        ```json title="settings.json"
        "yaml.schemas": {
            "https://squidfunk.github.io/mkdocs-material/schema.json": "mkdocs.yml"
        },
        "yaml.customTags": [ 
            "!ENV scalar",
            "!ENV sequence",
            "tag:yaml.org,2002:python/name:materialx.emoji.to_svg",
            "tag:yaml.org,2002:python/name:materialx.emoji.twemoji",
            "tag:yaml.org,2002:python/name:pymdownx.superfences.fence_code_format"
        ],
        ```

    3. [Customization](https://squidfunk.github.io/mkdocs-material/customization/){: target="_blank" .external }
        - Additional CSS and Javascript

            The easiest way is by creating a new style sheet file in the docs directory:

            ```graph title="directory structure"
            .
            ├─ docs/
            │  └─ mkdocs_stylesheets/
            │  │  └─ extra.css
            │  └─ mkdocs_javascripts/
            │     └─ extra.js
            └─ mkdocs.yml
            ```

            Then, add the following lines to mkdocs.yml:

            ```yaml title="mkdocs.yml"
            extra_css:
                - mkdocs_javascripts/extra.css
            extra_javascript:
                - mkdocs_javascripts/extra.js
            ```

        - Extending the theme

            Create a new folder for overrides which you then reference using the `custom_dir` setting:

            ```yaml title="mkdocs.yml"
            theme:
                name: material
                custom_dir: mkdocs_overrides
            ```

            The structure in the overrides directory must mirror the directory structure of the original theme, as any file in the overrides directory will replace the file with the same name which is part of the original theme.

        - Overriding Partials

            In order to override a partial, we can replace it with a file of the same name and location in the overrides directory. For example, to replace the original footer.html partial, create a new footer.html partial in the overrides directory:

            ```graph title="directory structure"
            .
            ├─ docs/
            ├─ mkdocs_overrides/
            │  └─ partials/
            │     └─ footer.html
            └─ mkdocs.yml
            ```

    4. [Material for MkDocs supported Python Markdonw](https://squidfunk.github.io/mkdocs-material/setup/extensions/python-markdown/){: target="_blank" .external }

        Material for MkDocs supports a large number of [Python Markdown](https://python-markdown.github.io/){: target="_blank" .external } extensions, which is part of what makes it so attractive for technical writing.

    5. [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/){: target="_blank" .external }

        PyMdown Extensions is a collection of extensions for Python Markdown. They were originally written to make writing documentation more enjoyable. They cover a wide range of solutions, and while not every extension is needed by all people, there is usually at least one useful extension for everybody.

        - Installation

            ```bat title="Install PyMdown"
            pip install pymdown-extensions
            ```

10. [mkdocs-minify-plugin](https://github.com/byrnereese/mkdocs-minify-plugin){: target="_blank" .external }

    An MkDocs plugin to minify HTML, JS or CSS files prior to being written to disk.

    - Setup
        - Install the plugin

            ```bat title="Install mkdocs-minify-plugin"
            pip install mkdocs-minify-plugin
            ```

        - Activate the plugin in mkdocs.yml:

            ```yaml title="mkdocs.yml"
            plugins:
            - search
            - minify:
                minify_html: true
                htmlmin_opts:
                    remove_comments: true
                cache_safe: true
            ```

11. Build MkDocs Site

    ```bat title="Build MkDocs Site"
    mkdocs build
    ```

## 参考サイト

### Django Framework

- [Django Project](https://www.djangoproject.com/){: target="_blank" .external }
- [Django Documentation](https://docs.djangoproject.com/en/4.1/){: target="_blank" .external }

##
### Python Language

- [Python](https://www.python.org/){: target="_blank" .external }
- [Python Developer’s Guide](https://devguide.python.org/){: target="_blank" .external }
- [Pip(Package installer for python)](https://pypi.org/project/pip/){: target="_blank" .external }
- [PyPI(Python Package Index)](https://pypi.org/){: target="_blank" .external }
- [Virtual Environment](https://docs.python.org/3/library/venv.html){: target="_blank" .external }
