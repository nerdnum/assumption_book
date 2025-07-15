<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

# ASSUMPTIONS-BACKEND.GIT

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)

---

## Overview

The backend employs the popular pyhon [fastapi](https://fastapi.tiangolo.com/) framework.

---

## Features

- User management with rolebased access to the app features
- Create a tree structure for the project components
- User create documentation regarding the project
- Documentation can be exported to docx and xlsx

---

## Project Structure

```sh
└── assumptions-backend.git/
    ├── DECISION_LOG.txt
    ├── README.md
    ├── alembic
    │   ├── README
    │   ├── env.py
    │   └── script.py.mako
    ├── alembic.ini
    ├── alembic_steps.text
    ├── alembichelp.py
    ├── app
    │   ├── __init__.py
    │   ├── config.py
    │   ├── html2docx
    │   ├── pydantic_models
    │   ├── services
    │   ├── sqlalchemy_models
    │   ├── static
    │   └── views
    ├── create_user_roles.py
    ├── http_request
    │   ├── components.rest
    │   ├── documents.rest
    │   ├── element_types.rest
    │   ├── elements.rest
    │   ├── projects.rest
    │   ├── risks
    │   ├── settings.rest
    │   └── user_projects_and_roles
    ├── pytest.ini
    ├── requirements.txt
    ├── run.py
    ├── t_e_s_t_backup
    │   ├── untest_02_element_types.py
    │   └── untest_03_elements.py
    ├── tests
    │   ├── 01_users_and_roles
    │   ├── 02_projects
    │   ├── 03_components
    │   ├── 04_documents
    │   ├── 05_settings
    │   ├── __init__.py
    │   ├── conftest.py
    │   └── utils.py
    └── utils
        ├── add_metrics.py
        ├── restructure-si-prefixes.py
        ├── si-prefixes.json
        ├── si-prefixes.txt
        └── slugify_components.py
```

### Project Index

<details open>
	<summary><b><code>ASSUMPTIONS-BACKEND.GIT/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/run.py'>run.py</a></b></td>
					<td style='padding: 8px;'>Run the project</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/create_user_roles.py'>create_user_roles.py</a></b></td>
					<td style='padding: 8px;'>A script that can be used to create roles directly in the DB from the command line.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/pytest.ini'>pytest.ini</a></b></td>
					<td style='padding: 8px;'>Testing init</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>Libraries used by the project and used by PIP to install all the dependencies</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/DECISION_LOG.txt'>DECISION_LOG.txt</a></b></td>
					<td style='padding: 8px;'>Good intention only :-)</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/alembic.ini'>alembic.ini</a></b></td>
					<td style='padding: 8px;'>For doing automated database migrations</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/alembichelp.py'>alembichelp.py</a></b></td>
					<td style='padding: 8px;'>Not used</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/alembic_steps.text'>alembic_steps.text</a></b></td>
					<td style='padding: 8px;'>A reminder of how to use alembic DB migration tool</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- app Submodule -->
	<details>
		<summary><b>app</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ app</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/config.py'>config.py</a></b></td>
					<td style='padding: 8px;'>Reads config.json file and makes it available to the broader project</td>
				</tr>
			</table>
			<!-- html2docx Submodule -->
			<details>
				<summary><b>html2docx</b></summary>
				<blockquote>
					Look at documention found at [html2docx](https://github.com/pqzx/html2docx)
				</blockquote>
			</details>
			<!-- sqlalchemy_models Submodule -->
			<details>
				<summary><b>sqlalchemy_models</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ app.sqlalchemy_models</b></code>
						<p>Contains all the models for reading and writing to the database. SqlAlchemy (DB ORM system) provides the database management functionality. Because users, roles and projects are so tightly coupled, the had to be put into one file to make the relationship definitions work.</p>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/sqlalchemy_models/documents_sql.py'>documents_sql.py</a></b></td>
							<td style='padding: 8px;'>For managing documents in the DB</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/sqlalchemy_models/settings_sql.py'>settings_sql.py</a></b></td>
							<td style='padding: 8px;'>For managing settings in the DB</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/sqlalchemy_models/setting_types_sql.py'>setting_types_sql.py</a></b></td>
							<td style='padding: 8px;'>For managing setting types in the DB</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/sqlalchemy_models/components_sql.py'>components_sql.py</a></b></td>
							<td style='padding: 8px;'>For managing components in the DB</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/sqlalchemy_models/user_project_role_sql.py'>user_project_role_sql.py</a></b></td>
							<td style='padding: 8px;'>For managing projects, users and roles in the DB</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- pydantic_models Submodule -->
			<details>
				<summary><b>pydantic_models</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ app.pydantic_models</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/document_model.py'>document_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for documents</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/user_model.py'>user_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for users</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/project_model.py'>project_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for projects</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/setting_model.py'>setting_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for settings</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/setting_type_model.py'>setting_type_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for setting types</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/component_model.py'>component_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for components</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/common_validators.py'>common_validators.py</a></b></td>
							<td style='padding: 8px;'>Validator that can be re-used across the pydantic models</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/pydantic_models/role_model.py'>role_model.py</a></b></td>
							<td style='padding: 8px;'>Pydantic models for roles</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- views Submodule -->
			<details>
				<summary><b>views</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ app.views</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/roles_view.py'>roles_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for roles</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/components_view.py'>components_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for components</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/setting_types_view.py'>setting_types_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for setting types</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/projects_view.py'>projects_view.py</a></b></td>
							<td style='padding: 8px;'>CAPI endpoints for projects</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/settings_view.py'>settings_view.py</a></b></td>
							<td style='padding: 8px;'>settings</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/doc_export_view.py'>doc_export_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for exporting documents</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/users_view.py'>users_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for users</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/documents_view.py'>documents_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for documents</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/websocket.py'>websocket.py</a></b></td>
							<td style='padding: 8px;'>Websocket endpoints used in the process of creating the export docx and xlsx</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/views/auth_view.py'>auth_view.py</a></b></td>
							<td style='padding: 8px;'>API endpoints for authentication</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- services Submodule -->
			<details>
				<summary><b>services</b></summary>
				<p>Supporting utilities</p>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ app.services</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/services/create_docx.py'>create_docx.py</a></b></td>
							<td style='padding: 8px;'>Create docx and xlsx files</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/services/database.py'>database.py</a></b></td>
							<td style='padding: 8px;'>Creates the async interface for sqlAlchemy</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/services/security.py'>security.py</a></b></td>
							<td style='padding: 8px;'>Not much in here - intended for authorisation features</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/app/services/utils.py'>utils.py</a></b></td>
							<td style='padding: 8px;'>Utilities used during development</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- utils Submodule -->
	<details>
		<summary><b>utils</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ utils</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/utils/restructure-si-prefixes.py'>restructure-si-prefixes.py</a></b></td>
					<td style='padding: 8px;'>Used during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/utils/si-prefixes.json'>si-prefixes.json</a></b></td>
					<td style='padding: 8px;'>Used during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/utils/slugify_components.py'>slugify_components.py</a></b></td>
					<td style='padding: 8px;'>Used during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/utils/si-prefixes.txt'>si-prefixes.txt</a></b></td>
					<td style='padding: 8px;'>Used during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/utils/add_metrics.py'>add_metrics.py</a></b></td>
					<td style='padding: 8px;'>Used during development</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- alembic Submodule -->
	<details>
		<summary><b>alembic</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ alembic</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/alembic/script.py.mako'>script.py.mako</a></b></td>
					<td style='padding: 8px;'>Not sure</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/alembic/env.py'>env.py</a></b></td>
					<td style='padding: 8px;'>Basis for the DB migrations</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- http_request Submodule -->
	<details>
		<summary><b>http_request</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ http_request</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/element_types.rest'>element_types.rest</a></b></td>
					<td style='padding: 8px;'>For manual testing during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/elements.rest'>elements.rest</a></b></td>
					<td style='padding: 8px;'>For manual testing during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/settings.rest'>settings.rest</a></b></td>
					<td style='padding: 8px;'>For manual testing during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/documents.rest'>documents.rest</a></b></td>
					<td style='padding: 8px;'>For manual testing during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/components.rest'>components.rest</a></b></td>
					<td style='padding: 8px;'>For manual testing during development</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/projects.rest'>projects.rest</a></b></td>
					<td style='padding: 8px;'>For manual testing during development</td>
				</tr>
			</table>
			<!-- user_projects_and_roles Submodule -->
			<details>
				<summary><b>user_projects_and_roles</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ http_request.user_projects_and_roles</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/user_projects_and_roles/users.rest'>users.rest</a></b></td>
							<td style='padding: 8px;'>For manual testing during development</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/user_projects_and_roles/project_roles.rest'>project_roles.rest</a></b></td>
							<td style='padding: 8px;'>For manual testing during development</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/user_projects_and_roles/roles.rest'>roles.rest</a></b></td>
							<td style='padding: 8px;'>For manual testing during development</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/user_projects_and_roles/user_projects.rest'>user_projects.rest</a></b></td>
							<td style='padding: 8px;'>For manual testing during development</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/CWPTech/assumptions-backend.git/blob/master/http_request/user_projects_and_roles/user_and_roles.rest'>user_and_roles.rest</a></b></td>
							<td style='padding: 8px;'>For manual testing during development</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip

### Installation

Build assumptions-backend.git from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/CWPTech/assumptions-backend.git
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd assumptions-backend.git
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![pip][pip-shield]][pip-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [pip-shield]: https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white -->
	<!-- [pip-link]: https://pypi.org/project/pip/ -->

	**Using [pip](https://pypi.org/project/pip/):**

	```sh
	❯ pip install -r requirements.txt
	```
The ```app/html2docx``` folder is a clone of the html2docx project [html2docx](https://github.com/pqzx/html2docx). Unfortunately the reason for using the cloned folder instead of the most recent version of the library is lost.

### Usage

Run the project in development mode with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
uvicorn run:server 
```

### Testing

Assumptions-backend.git uses the [pytest](https://docs.pytest.org/en/stable/) testing framework. Run the test suite with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
pytest
```

Towards the end of development, the test files for the API was not kept up to date, so most of the test are likely to fail, however, it can provide a good starting point for testing as the core configuration is done.

---


## License

This project was developed for CWP Global.

---


<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
