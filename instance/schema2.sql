CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE expertise_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE lists (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE product_groups (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE list_items (
	id INTEGER NOT NULL, 
	list_id INTEGER NOT NULL, 
	value VARCHAR(100) NOT NULL, 
	description TEXT, 
	"order" INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(list_id) REFERENCES lists (id) ON DELETE CASCADE
);
CREATE TABLE products_services (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	type VARCHAR(20) NOT NULL, 
	group_id INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES product_groups (id) ON DELETE CASCADE
);
CREATE TABLE clients (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	address VARCHAR(200), 
	city VARCHAR(100), 
	country_id INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, sales_person VARCHAR(100), project_manager VARCHAR(100), active BOOLEAN DEFAULT 1, industry VARCHAR(100), 
	PRIMARY KEY (id), 
	FOREIGN KEY(country_id) REFERENCES list_items (id)
);
CREATE TABLE project_templates (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	client_id INTEGER, 
	manager_id INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(client_id) REFERENCES clients (id), 
	FOREIGN KEY(manager_id) REFERENCES users (id)
);
CREATE TABLE phase_templates (
	id INTEGER NOT NULL, 
	template_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	"order" INTEGER NOT NULL, 
	duration_days INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(template_id) REFERENCES project_templates (id)
);
CREATE TABLE projects (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	template_id INTEGER, 
	client_id INTEGER, 
	manager_id INTEGER, 
	start_date DATE, 
	end_date DATE, 
	status VARCHAR(20), 
	created_at DATETIME, 
	updated_at DATETIME, industry_id INTEGER REFERENCES list_items(id), profit_center_id INTEGER REFERENCES list_items(id), 
	PRIMARY KEY (id), 
	FOREIGN KEY(client_id) REFERENCES clients (id), 
	FOREIGN KEY(manager_id) REFERENCES users (id), 
	FOREIGN KEY(template_id) REFERENCES project_templates (id)
);
CREATE TABLE template_products (
	template_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	PRIMARY KEY (template_id, product_id), 
	FOREIGN KEY(product_id) REFERENCES products_services (id) ON DELETE CASCADE, 
	FOREIGN KEY(template_id) REFERENCES project_templates (id) ON DELETE CASCADE
);
CREATE TABLE project_products (
	project_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	PRIMARY KEY (project_id, product_id), 
	FOREIGN KEY(product_id) REFERENCES products_services (id) ON DELETE CASCADE, 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(20) NOT NULL, 
	description VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE user_roles (
	user_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, role_id), 
	FOREIGN KEY(role_id) REFERENCES roles (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE IF NOT EXISTS "users" (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128), 
	first_name VARCHAR(50), 
	last_name VARCHAR(50), 
	created_at DATETIME, 
	is_active BOOLEAN, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	UNIQUE (username)
);
CREATE TABLE IF NOT EXISTS "consultants" (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	availability_days_per_month INTEGER, 
	status VARCHAR(20), 
	start_date DATE, 
	end_date DATE, 
	notes TEXT, 
	calendar_name VARCHAR(100), 
	created_at DATETIME, 
	updated_at DATETIME, custom_data JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE product_elements (
	id INTEGER NOT NULL, 
	label VARCHAR(100) NOT NULL, 
	activity VARCHAR(255) NOT NULL, 
	group_id INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES product_groups (id) ON DELETE CASCADE
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE consultants_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'Active'
    );
CREATE TABLE IF NOT EXISTS "consultant_expertise" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultant_id INTEGER NOT NULL,
    product_group_id INTEGER,
    product_element_id INTEGER,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    notes TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultant_id) REFERENCES consultants (id) ON DELETE CASCADE,
    FOREIGN KEY (product_group_id) REFERENCES product_groups (id) ON DELETE CASCADE,
    FOREIGN KEY (product_element_id) REFERENCES product_elements (id) ON DELETE CASCADE
);
CREATE TABLE project_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    product_group_id INTEGER NOT NULL,
                    "order" INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_group_id) REFERENCES product_groups(id)
                );
CREATE TABLE project_phases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    duration_id INTEGER,
                    online BOOLEAN DEFAULT 0,
                    "order" INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES project_groups(id) ON DELETE CASCADE,
                    FOREIGN KEY (duration_id) REFERENCES list_items(id)
                );
