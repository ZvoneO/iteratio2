PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('49ee78684880');
CREATE TABLE expertise_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO expertise_categories VALUES(1,'Java',NULL,'2025-03-07 06:24:14.840946','2025-03-07 06:24:14.840949');
INSERT INTO expertise_categories VALUES(2,'Python',NULL,'2025-03-07 06:24:14.841590','2025-03-07 06:24:14.841592');
INSERT INTO expertise_categories VALUES(3,'JavaScript',NULL,'2025-03-07 06:24:14.841992','2025-03-07 06:24:14.841994');
INSERT INTO expertise_categories VALUES(4,'DevOps',NULL,'2025-03-07 06:24:14.842369','2025-03-07 06:24:14.842371');
INSERT INTO expertise_categories VALUES(5,'Database',NULL,'2025-03-07 06:24:14.842746','2025-03-07 06:24:14.842748');
INSERT INTO expertise_categories VALUES(6,'Cloud',NULL,'2025-03-07 06:24:14.843057','2025-03-07 06:24:14.843059');
CREATE TABLE lists (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO lists VALUES(1,'PhaseDuration','Values for Phase duration','2025-03-06 13:05:21.629901','2025-03-06 13:05:21.629904');
INSERT INTO lists VALUES(2,'ProfitCenter','','2025-03-06 14:30:41.816472','2025-03-06 14:30:41.816474');
CREATE TABLE product_groups (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO product_groups VALUES(1,'ALP I','Adizes Leadership Program I','2025-03-07 15:05:42.756976','2025-03-07 15:05:42.756985');
INSERT INTO product_groups VALUES(2,'ALP II','Adizes Leadership Program II','2025-03-07 15:06:01.285755','2025-03-07 15:06:01.285757');
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
INSERT INTO list_items VALUES(1,2,'UP','Unapređenje poslovanja',1,'2025-03-06 14:30:41.820778','2025-03-06 14:30:41.820780');
INSERT INTO list_items VALUES(2,2,'APZ','Aktivacija potencijala zaposlenih',2,'2025-03-06 14:30:41.820782','2025-03-06 14:30:41.820782');
INSERT INTO list_items VALUES(3,2,'Ch.Pr.','Challenging Practice',3,'2025-03-06 14:30:41.820783','2025-03-06 14:30:41.820784');
INSERT INTO list_items VALUES(4,2,'Klijenti','Klijenti',4,'2025-03-06 14:30:41.820784','2025-03-06 14:30:41.820785');
INSERT INTO list_items VALUES(5,2,'AI','Adizes Institute',5,'2025-03-06 14:30:41.820786','2025-03-06 14:30:41.820786');
INSERT INTO list_items VALUES(6,2,'FB','Family Business',6,'2025-03-06 14:30:41.820787','2025-03-06 14:30:41.820788');
INSERT INTO list_items VALUES(7,2,'ASEE','ASEE',7,'2025-03-06 14:30:41.820788','2025-03-06 14:30:41.820789');
INSERT INTO list_items VALUES(8,1,'0,3','1/3 dana',1,'2025-03-06 14:31:26.832941','2025-03-06 14:31:26.832944');
INSERT INTO list_items VALUES(9,1,'0,5','pola dana',2,'2025-03-06 14:31:26.832945','2025-03-06 14:31:26.832946');
INSERT INTO list_items VALUES(10,1,'1','dan',3,'2025-03-06 14:31:26.832947','2025-03-06 14:31:26.832948');
INSERT INTO list_items VALUES(11,1,'2','2 dana',4,'2025-03-06 14:31:26.832949','2025-03-06 14:31:26.832950');
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
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(country_id) REFERENCES list_items (id)
);
INSERT INTO clients VALUES(1,'ASEE','','Beograd',NULL,'2025-03-05 18:41:24.796366','2025-03-05 18:41:24.796368');
INSERT INTO clients VALUES(2,'Agromarket','','Kragujevac',NULL,'2025-03-05 18:41:24.797135','2025-03-05 18:41:24.797136');
INSERT INTO clients VALUES(3,'AGS','','Split',NULL,'2025-03-05 18:41:24.797532','2025-03-05 18:41:24.797534');
INSERT INTO clients VALUES(4,'AI Solution','','Podgorica',NULL,'2025-03-05 18:41:24.797917','2025-03-05 18:41:24.797918');
INSERT INTO clients VALUES(5,'Akvapan','','Čačak',NULL,'2025-03-05 18:41:24.798318','2025-03-05 18:41:24.798320');
INSERT INTO clients VALUES(6,'Alfaterm','','Mostar',NULL,'2025-03-05 18:41:24.798704','2025-03-05 18:41:24.798706');
INSERT INTO clients VALUES(7,'Aling Conel','','Gajdobra',NULL,'2025-03-05 18:41:24.799362','2025-03-05 18:41:24.799365');
INSERT INTO clients VALUES(8,'Alliance','','Podgorica',NULL,'2025-03-05 18:41:24.800091','2025-03-05 18:41:24.800093');
INSERT INTO clients VALUES(9,'AlmaRas','','Olovo',NULL,'2025-03-05 18:41:24.800548','2025-03-05 18:41:24.800550');
INSERT INTO clients VALUES(10,'Anđelković','','Vinča',NULL,'2025-03-05 18:41:24.802017','2025-03-05 18:41:24.802019');
INSERT INTO clients VALUES(11,'Asura Group','','Zagreb',NULL,'2025-03-05 18:41:24.802450','2025-03-05 18:41:24.802452');
INSERT INTO clients VALUES(12,'Atlas','','Sevojno',NULL,'2025-03-05 18:41:24.802874','2025-03-05 18:41:24.802876');
INSERT INTO clients VALUES(13,'Auto Čačak Komerc','','Čačak',NULL,'2025-03-05 18:41:24.803342','2025-03-05 18:41:24.803344');
INSERT INTO clients VALUES(14,'Automaterijal','','Šabac',NULL,'2025-03-05 18:41:24.803770','2025-03-05 18:41:24.803772');
INSERT INTO clients VALUES(15,'Bosil','','Vitez',NULL,'2025-03-05 18:41:24.804420','2025-03-05 18:41:24.804421');
INSERT INTO clients VALUES(16,'Byte Lab Grupa','','Zagreb',NULL,'2025-03-05 18:41:24.804769','2025-03-05 18:41:24.804770');
CREATE TABLE consultant_expertise (
	id INTEGER NOT NULL, 
	consultant_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	rating INTEGER NOT NULL, 
	notes TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES expertise_categories (id) ON DELETE CASCADE, 
	FOREIGN KEY(consultant_id) REFERENCES consultants (id) ON DELETE CASCADE
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
	updated_at DATETIME, 
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
INSERT INTO roles VALUES(1,'Admin',NULL);
INSERT INTO roles VALUES(2,'Manager',NULL);
INSERT INTO roles VALUES(3,'Project Manager',NULL);
INSERT INTO roles VALUES(4,'Consultant',NULL);
CREATE TABLE user_roles (
	user_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, role_id), 
	FOREIGN KEY(role_id) REFERENCES roles (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO user_roles VALUES(1,4);
INSERT INTO user_roles VALUES(1,1);
INSERT INTO user_roles VALUES(2,1);
INSERT INTO user_roles VALUES(2,2);
INSERT INTO user_roles VALUES(2,3);
INSERT INTO user_roles VALUES(2,4);
INSERT INTO user_roles VALUES(6,4);
INSERT INTO user_roles VALUES(3,1);
INSERT INTO user_roles VALUES(7,4);
INSERT INTO user_roles VALUES(7,2);
INSERT INTO user_roles VALUES(3,4);
INSERT INTO user_roles VALUES(4,4);
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
INSERT INTO users VALUES(1,'admin','admin@example.com','scrypt:32768:8:1$mveAAcYQR8VBx5JF$e2dbe9243c6e9b0869a66f1d14b1a254719ef42e45941c91718a899fef38d937bde4b407a12e1fef9c6af34bb1944e7be009f84ab82bf22973f51387f4597b4c','Admin','User','2025-03-05 10:55:31.761247',1,'2025-03-05 15:09:37.021098');
INSERT INTO users VALUES(2,'zvoneo','zvonimir.orec@servitio.hr','scrypt:32768:8:1$CP4By88FUVwgxTnr$2a3cdafa2477bb45eb79718dd1e4c3d97d1390cf942fc18d990fc25861766a8048f0156f6d2e183ccd3ee5d207c9277201c06884ed6a6c04f72a22bfac173c27','Zvonimir','Oreč','2025-03-05 11:12:08.256821',1,'2025-03-07 02:36:14.116096');
INSERT INTO users VALUES(3,'admin@asee.rs','admin@asee.rs','scrypt:32768:8:1$6adn9t2Pgr4aP4vv$f14250de5e6d4f493279383b2031592bba188f23f52afff4a65eeca4d92d43bc136d5b82903d33a4805a9d6adcb7bae40742ba14ca35b19947d0cfc78c0aff08','Admin','','2025-03-05 14:41:02.908460',1,'2025-03-05 18:27:03.904637');
INSERT INTO users VALUES(4,'testconsultant','test@test.com','scrypt:32768:8:1$lEhQf7OFobGHTWRW$a86a97686e332b1a0195412667f5825cdf6bb572b6e1d2d0a4dfaceb4c409ea93691aa29696fc806329b9edf586c0358acf6614f65631cc2a556fe0df24900f4','Test','konzo','2025-03-06 11:07:23.109259',1,'2025-03-06 11:07:23.109263');
INSERT INTO users VALUES(6,'newcons','newcons@mail.com','scrypt:32768:8:1$ppZtZzGy1XGkIEF0$6bd7f632ae660967a96352f301c4850e0f8f6d4976d91aeb2d71915d282d75260f0d774881a9d3ae7a9c49447680a0ff67190a5a7de753b9c571123723a0a820','New','Cons','2025-03-07 08:16:42.579097',1,'2025-03-07 08:16:42.579101');
INSERT INTO users VALUES(7,'admin22','zvonimir2@servitio.hr','scrypt:32768:8:1$d99cZcYD8QcM2o6M$1b0f97b49c3656f3a4827afca0ffbc8afca2f405d4898f86d523bf8a1b00829a9caf976afc2aa9b2dc2f36e423cc27b527422549c6bf149317447ac8277e6a84','Zv ','O ','2025-03-07 12:31:16.538888',1,'2025-03-07 12:31:16.538893');
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
INSERT INTO consultants VALUES(2,1,0,'Active',NULL,NULL,NULL,NULL,'2025-03-07 07:58:49.848408','2025-03-07 07:58:49.848411',NULL);
INSERT INTO consultants VALUES(3,3,0,'Active',NULL,NULL,NULL,NULL,'2025-03-07 07:58:49.850423','2025-03-07 07:58:49.850425',NULL);
INSERT INTO consultants VALUES(5,2,0,'Active',NULL,NULL,NULL,NULL,'2025-03-07 07:58:49.851349','2025-03-08 05:43:26.455166','{"expertise": {"product_group_1": {"type": "product_group", "id": "1", "rating": 4, "notes": ""}}}');
INSERT INTO consultants VALUES(6,6,0,'Inactive',NULL,NULL,'None','None','2025-03-07 08:19:44.680325','2025-03-08 05:46:00.688359','{"expertise": {"product_group_2": {"type": "product_group", "id": "2", "rating": 3, "notes": ""}}}');
INSERT INTO consultants VALUES(7,7,12,'Active','2025-01-01','2025-03-11',NULL,NULL,'2025-03-07 12:31:34.488670','2025-03-07 12:32:11.540619',NULL);
INSERT INTO consultants VALUES(8,4,0,'Active',NULL,NULL,NULL,NULL,'2025-03-08 04:54:19.172416','2025-03-08 04:54:19.172419',NULL);
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
INSERT INTO product_elements VALUES(1,'ALP I - 1','Modul 1',1,'2025-03-07 15:41:27.090108','2025-03-07 15:41:27.090112');
INSERT INTO product_elements VALUES(2,'ALP I - 2','Modul 2',1,'2025-03-07 15:41:27.090113','2025-03-07 15:41:27.090114');
INSERT INTO product_elements VALUES(3,'ALP I - 3','Modul 3',1,'2025-03-07 15:41:27.090115','2025-03-07 15:41:27.090116');
INSERT INTO product_elements VALUES(4,'ALP I - 4','Modul 4',1,'2025-03-07 15:41:27.090116','2025-03-07 15:41:27.090117');
INSERT INTO product_elements VALUES(5,'ALP I - 5','Modul 5',1,'2025-03-07 15:41:27.090118','2025-03-07 15:41:27.090119');
INSERT INTO product_elements VALUES(6,'ALP I - 6','Modul 6',1,'2025-03-07 15:41:27.090120','2025-03-07 15:41:27.090121');
INSERT INTO product_elements VALUES(7,'ALP I - 7','Modul 7',1,'2025-03-07 15:41:27.090121','2025-03-07 15:41:27.090122');
INSERT INTO product_elements VALUES(8,'ALP I - 8','Modul 8',1,'2025-03-07 15:41:27.090123','2025-03-07 15:41:27.090124');
INSERT INTO product_elements VALUES(9,'ALP II - 1','Sindag',2,'2025-03-08 05:47:35.188493','2025-03-08 05:47:35.188496');
INSERT INTO product_elements VALUES(10,'ALP II - 2','Timovi',2,'2025-03-08 05:47:35.188497','2025-03-08 05:47:35.188498');
INSERT INTO product_elements VALUES(11,'ALP II - 3','Misija',2,'2025-03-08 05:47:35.188499','2025-03-08 05:47:35.188500');
INSERT INTO product_elements VALUES(12,'ALP II - 4','Struktura',2,'2025-03-08 05:47:35.188501','2025-03-08 05:47:35.188501');
INSERT INTO product_elements VALUES(13,'ALP II - 5','Ciljevi',2,'2025-03-08 05:47:35.188502','2025-03-08 05:47:35.188503');
INSERT INTO product_elements VALUES(14,'ALP II - 6','Budžet',2,'2025-03-08 05:47:35.188504','2025-03-08 05:47:35.188505');
INSERT INTO product_elements VALUES(15,'ALP II - 7','Nagrađivanje',2,'2025-03-08 05:47:35.188506','2025-03-08 05:47:35.188507');
INSERT INTO product_elements VALUES(16,'ALP II - 8','Ispit',2,'2025-03-08 05:47:35.188507','2025-03-08 05:47:35.188508');
COMMIT;
