-- Vunoh AI Internship Practical Test SQL dump
-- Generated via `python manage.py export_sql_dump`

BEGIN TRANSACTION;
CREATE TABLE "assistant_statushistory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "old_status" varchar(16) NOT NULL, "new_status" varchar(16) NOT NULL, "changed_at" datetime NOT NULL, "changed_by" varchar(64) NOT NULL, "task_id" bigint NOT NULL REFERENCES "assistant_task" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "assistant_statushistory" VALUES(1,'','PENDING','2026-04-16 12:47:09.713303','system',1);
INSERT INTO "assistant_statushistory" VALUES(2,'PENDING','IN_PROGRESS','2026-04-16 12:48:35.833773','customer',1);
INSERT INTO "assistant_statushistory" VALUES(3,'','PENDING','2026-04-18 18:04:08.706288','system',2);
INSERT INTO "assistant_statushistory" VALUES(4,'','PENDING','2026-04-18 18:04:08.966730','system',3);
INSERT INTO "assistant_statushistory" VALUES(5,'','PENDING','2026-04-18 18:04:09.048360','system',4);
INSERT INTO "assistant_statushistory" VALUES(6,'','PENDING','2026-04-18 18:04:09.121300','system',5);
CREATE TABLE "assistant_task" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "task_code" varchar(64) NOT NULL UNIQUE, "client_id" varchar(64) NOT NULL, "customer_request" text NOT NULL, "intent" varchar(32) NOT NULL, "entities" text NOT NULL CHECK ((JSON_VALID("entities") OR "entities" IS NULL)), "risk_score" integer NOT NULL, "status" varchar(16) NOT NULL, "assigned_team" varchar(16) NOT NULL, "ai_model" varchar(128) NOT NULL, "prompt_version" varchar(64) NOT NULL, "created_at" datetime NOT NULL, "reference_task_code" varchar(64) NULL);
INSERT INTO "assistant_task" VALUES(1,'VG-20260416-21242','test_client_1','I need to send KES 15000 to my mother in Kisumu urgently.','send_money','{"amount_kes": 15000, "recipient_name": null, "recipient_location": "Kisumu", "recipient_bank_or_method": null, "urgency": "urgent", "pickup_location": null, "arrival_time": null, "passenger_name": null, "vehicle_type": null, "service_type": null, "location": null, "scheduled_date": null, "scheduled_time": null, "document_type": null, "document_reference": null, "task_code": null, "reference": null}',55,'IN_PROGRESS','FINANCE','','day2_v1','2026-04-16 12:47:09.703836',NULL);
INSERT INTO "assistant_task" VALUES(2,'VG-20260418-59422','sample_client_001','I need to send KES 15,000 to my mother in Kisumu urgently.','send_money','{"amount_kes": 15000, "recipient_name": null, "recipient_location": "Kisumu", "recipient_bank_or_method": null, "urgency": "urgent", "pickup_location": null, "arrival_time": null, "passenger_name": null, "vehicle_type": null, "service_type": null, "location": null, "scheduled_date": null, "scheduled_time": null, "document_type": null, "document_reference": null, "task_code": null, "reference": null}',55,'PENDING','FINANCE','','seed_v1','2026-04-18 18:04:08.682265',NULL);
INSERT INTO "assistant_task" VALUES(3,'VG-20260418-37031','sample_client_001','Please verify my land title deed for the plot in Karen.','verify_document','{"amount_kes": null, "recipient_name": null, "recipient_location": null, "recipient_bank_or_method": null, "urgency": null, "pickup_location": null, "arrival_time": null, "passenger_name": null, "vehicle_type": null, "service_type": null, "location": "Karen", "scheduled_date": null, "scheduled_time": null, "document_type": "land_title_deed", "document_reference": null, "task_code": null, "reference": null}',60,'PENDING','LEGAL','','seed_v1','2026-04-18 18:04:08.947269',NULL);
INSERT INTO "assistant_task" VALUES(4,'VG-20260418-67226','sample_client_001','Can someone clean my apartment in Westlands on Friday at 10am?','hire_service','{"amount_kes": null, "recipient_name": null, "recipient_location": null, "recipient_bank_or_method": null, "urgency": null, "pickup_location": null, "arrival_time": null, "passenger_name": null, "vehicle_type": null, "service_type": "cleaner", "location": "Westlands on Friday at", "scheduled_date": "Friday", "scheduled_time": "10am", "document_type": null, "document_reference": null, "task_code": null, "reference": null}',10,'PENDING','OPERATIONS','','seed_v1','2026-04-18 18:04:09.032357',NULL);
INSERT INTO "assistant_task" VALUES(5,'VG-20260418-13183','sample_client_001','I need an airport pickup in Nairobi for arrival at 7pm tonight.','get_airport_transfer','{"amount_kes": null, "recipient_name": null, "recipient_location": null, "recipient_bank_or_method": null, "urgency": "urgent", "pickup_location": "Nairobi for arrival at", "arrival_time": null, "passenger_name": null, "vehicle_type": null, "service_type": null, "location": null, "scheduled_date": null, "scheduled_time": null, "document_type": null, "document_reference": null, "task_code": null, "reference": null}',45,'PENDING','OPERATIONS','','seed_v1','2026-04-18 18:04:09.105891',NULL);
CREATE TABLE "assistant_taskmessage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "channel" varchar(16) NOT NULL, "subject" varchar(200) NOT NULL, "message_text" text NOT NULL, "task_id" bigint NOT NULL REFERENCES "assistant_task" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "assistant_taskmessage" VALUES(1,'WHATSAPP','','Hi! We received your request.
Task code: VG-20260416-21242
We will handle it shortly.',1);
INSERT INTO "assistant_taskmessage" VALUES(2,'EMAIL','Vunoh Global - Task VG-20260416-21242 created','Hello,

Your request has been received and a task has been created.
Task code: VG-20260416-21242
Intent: send_money

We’ll update you as the steps progress.
',1);
INSERT INTO "assistant_taskmessage" VALUES(3,'SMS','','VG-20260416-21242: we started your send money request. Reply for updates.',1);
INSERT INTO "assistant_taskmessage" VALUES(4,'WHATSAPP','','Hi! We received your request.
Task code: VG-20260418-59422
We will handle it shortly.',2);
INSERT INTO "assistant_taskmessage" VALUES(5,'EMAIL','Vunoh Global - Task VG-20260418-59422 created','Hello,

Your request has been received and a task has been created.
Task code: VG-20260418-59422
Intent: send_money

We’ll update you as the steps progress.
',2);
INSERT INTO "assistant_taskmessage" VALUES(6,'SMS','','VG-20260418-59422: we started your send money request. Reply for updates.',2);
INSERT INTO "assistant_taskmessage" VALUES(7,'WHATSAPP','','Hi! We received your request.
Task code: VG-20260418-37031
We will handle it shortly.',3);
INSERT INTO "assistant_taskmessage" VALUES(8,'EMAIL','Vunoh Global - Task VG-20260418-37031 created','Hello,

Your request has been received and a task has been created.
Task code: VG-20260418-37031
Intent: verify_document

We’ll update you as the steps progress.
',3);
INSERT INTO "assistant_taskmessage" VALUES(9,'SMS','','VG-20260418-37031: we started your verify document request. Reply for updates.',3);
INSERT INTO "assistant_taskmessage" VALUES(10,'WHATSAPP','','Hi! We received your request.
Task code: VG-20260418-67226
We will handle it shortly.',4);
INSERT INTO "assistant_taskmessage" VALUES(11,'EMAIL','Vunoh Global - Task VG-20260418-67226 created','Hello,

Your request has been received and a task has been created.
Task code: VG-20260418-67226
Intent: hire_service

We’ll update you as the steps progress.
',4);
INSERT INTO "assistant_taskmessage" VALUES(12,'SMS','','VG-20260418-67226: we started your hire service request. Reply for updates.',4);
INSERT INTO "assistant_taskmessage" VALUES(13,'WHATSAPP','','Hi! We received your request.
Task code: VG-20260418-13183
We will handle it shortly.',5);
INSERT INTO "assistant_taskmessage" VALUES(14,'EMAIL','Vunoh Global - Task VG-20260418-13183 created','Hello,

Your request has been received and a task has been created.
Task code: VG-20260418-13183
Intent: get_airport_transfer

We’ll update you as the steps progress.
',5);
INSERT INTO "assistant_taskmessage" VALUES(15,'SMS','','VG-20260418-13183: we started your get airport transfer request. Reply for updates.',5);
CREATE TABLE "assistant_taskstep" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "step_order" integer unsigned NOT NULL CHECK ("step_order" >= 0), "step_text" text NOT NULL, "task_id" bigint NOT NULL REFERENCES "assistant_task" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "assistant_taskstep" VALUES(1,1,'Confirm recipient details (name/location).',1);
INSERT INTO "assistant_taskstep" VALUES(2,2,'Verify urgency and amount for the transfer.',1);
INSERT INTO "assistant_taskstep" VALUES(3,3,'Run identity checks for the requester and recipient.',1);
INSERT INTO "assistant_taskstep" VALUES(4,4,'Initiate the transfer and share confirmation.',1);
INSERT INTO "assistant_taskstep" VALUES(5,5,'Provide final status update to you.',1);
INSERT INTO "assistant_taskstep" VALUES(6,1,'Confirm recipient details (name/location).',2);
INSERT INTO "assistant_taskstep" VALUES(7,2,'Verify urgency and amount for the transfer.',2);
INSERT INTO "assistant_taskstep" VALUES(8,3,'Run identity checks for the requester and recipient.',2);
INSERT INTO "assistant_taskstep" VALUES(9,4,'Initiate the transfer and share confirmation.',2);
INSERT INTO "assistant_taskstep" VALUES(10,5,'Provide final status update to you.',2);
INSERT INTO "assistant_taskstep" VALUES(11,1,'Confirm the document type and reference you provided.',3);
INSERT INTO "assistant_taskstep" VALUES(12,2,'Validate ownership/format requirements for verification.',3);
INSERT INTO "assistant_taskstep" VALUES(13,3,'Perform verification checks and validate relevant records.',3);
INSERT INTO "assistant_taskstep" VALUES(14,4,'Return results with next actions (if any).',3);
INSERT INTO "assistant_taskstep" VALUES(15,1,'Confirm service type and location details.',4);
INSERT INTO "assistant_taskstep" VALUES(16,2,'Match with available local service providers.',4);
INSERT INTO "assistant_taskstep" VALUES(17,3,'Schedule at your requested date/time.',4);
INSERT INTO "assistant_taskstep" VALUES(18,4,'Share provider confirmation and instructions.',4);
INSERT INTO "assistant_taskstep" VALUES(19,5,'Collect sign-off when service is complete.',4);
INSERT INTO "assistant_taskstep" VALUES(20,1,'Confirm pickup location and arrival details.',5);
INSERT INTO "assistant_taskstep" VALUES(21,2,'Assign an available driver/partner for the trip.',5);
INSERT INTO "assistant_taskstep" VALUES(22,3,'Share confirmation and pickup instructions.',5);
INSERT INTO "assistant_taskstep" VALUES(23,4,'Confirm completion of the transfer.',5);
CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);
CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);
INSERT INTO "auth_permission" VALUES(1,1,'add_logentry','Can add log entry');
INSERT INTO "auth_permission" VALUES(2,1,'change_logentry','Can change log entry');
INSERT INTO "auth_permission" VALUES(3,1,'delete_logentry','Can delete log entry');
INSERT INTO "auth_permission" VALUES(4,1,'view_logentry','Can view log entry');
INSERT INTO "auth_permission" VALUES(5,3,'add_permission','Can add permission');
INSERT INTO "auth_permission" VALUES(6,3,'change_permission','Can change permission');
INSERT INTO "auth_permission" VALUES(7,3,'delete_permission','Can delete permission');
INSERT INTO "auth_permission" VALUES(8,3,'view_permission','Can view permission');
INSERT INTO "auth_permission" VALUES(9,2,'add_group','Can add group');
INSERT INTO "auth_permission" VALUES(10,2,'change_group','Can change group');
INSERT INTO "auth_permission" VALUES(11,2,'delete_group','Can delete group');
INSERT INTO "auth_permission" VALUES(12,2,'view_group','Can view group');
INSERT INTO "auth_permission" VALUES(13,4,'add_user','Can add user');
INSERT INTO "auth_permission" VALUES(14,4,'change_user','Can change user');
INSERT INTO "auth_permission" VALUES(15,4,'delete_user','Can delete user');
INSERT INTO "auth_permission" VALUES(16,4,'view_user','Can view user');
INSERT INTO "auth_permission" VALUES(17,5,'add_contenttype','Can add content type');
INSERT INTO "auth_permission" VALUES(18,5,'change_contenttype','Can change content type');
INSERT INTO "auth_permission" VALUES(19,5,'delete_contenttype','Can delete content type');
INSERT INTO "auth_permission" VALUES(20,5,'view_contenttype','Can view content type');
INSERT INTO "auth_permission" VALUES(21,6,'add_session','Can add session');
INSERT INTO "auth_permission" VALUES(22,6,'change_session','Can change session');
INSERT INTO "auth_permission" VALUES(23,6,'delete_session','Can delete session');
INSERT INTO "auth_permission" VALUES(24,6,'view_session','Can view session');
INSERT INTO "auth_permission" VALUES(25,8,'add_task','Can add task');
INSERT INTO "auth_permission" VALUES(26,8,'change_task','Can change task');
INSERT INTO "auth_permission" VALUES(27,8,'delete_task','Can delete task');
INSERT INTO "auth_permission" VALUES(28,8,'view_task','Can view task');
INSERT INTO "auth_permission" VALUES(29,7,'add_statushistory','Can add status history');
INSERT INTO "auth_permission" VALUES(30,7,'change_statushistory','Can change status history');
INSERT INTO "auth_permission" VALUES(31,7,'delete_statushistory','Can delete status history');
INSERT INTO "auth_permission" VALUES(32,7,'view_statushistory','Can view status history');
INSERT INTO "auth_permission" VALUES(33,9,'add_taskmessage','Can add task message');
INSERT INTO "auth_permission" VALUES(34,9,'change_taskmessage','Can change task message');
INSERT INTO "auth_permission" VALUES(35,9,'delete_taskmessage','Can delete task message');
INSERT INTO "auth_permission" VALUES(36,9,'view_taskmessage','Can view task message');
INSERT INTO "auth_permission" VALUES(37,10,'add_taskstep','Can add task step');
INSERT INTO "auth_permission" VALUES(38,10,'change_taskstep','Can change task step');
INSERT INTO "auth_permission" VALUES(39,10,'delete_taskstep','Can delete task step');
INSERT INTO "auth_permission" VALUES(40,10,'view_taskstep','Can view task step');
CREATE TABLE "auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "first_name" varchar(150) NOT NULL);
CREATE TABLE "auth_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "auth_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);
CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
INSERT INTO "django_content_type" VALUES(1,'admin','logentry');
INSERT INTO "django_content_type" VALUES(2,'auth','group');
INSERT INTO "django_content_type" VALUES(3,'auth','permission');
INSERT INTO "django_content_type" VALUES(4,'auth','user');
INSERT INTO "django_content_type" VALUES(5,'contenttypes','contenttype');
INSERT INTO "django_content_type" VALUES(6,'sessions','session');
INSERT INTO "django_content_type" VALUES(7,'assistant','statushistory');
INSERT INTO "django_content_type" VALUES(8,'assistant','task');
INSERT INTO "django_content_type" VALUES(9,'assistant','taskmessage');
INSERT INTO "django_content_type" VALUES(10,'assistant','taskstep');
CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);
INSERT INTO "django_migrations" VALUES(1,'contenttypes','0001_initial','2026-04-16 12:33:35.733022');
INSERT INTO "django_migrations" VALUES(2,'auth','0001_initial','2026-04-16 12:33:35.769570');
INSERT INTO "django_migrations" VALUES(3,'admin','0001_initial','2026-04-16 12:33:35.798112');
INSERT INTO "django_migrations" VALUES(4,'admin','0002_logentry_remove_auto_add','2026-04-16 12:33:35.825063');
INSERT INTO "django_migrations" VALUES(5,'admin','0003_logentry_add_action_flag_choices','2026-04-16 12:33:35.840615');
INSERT INTO "django_migrations" VALUES(6,'assistant','0001_initial','2026-04-16 12:33:35.877087');
INSERT INTO "django_migrations" VALUES(7,'contenttypes','0002_remove_content_type_name','2026-04-16 12:33:35.929024');
INSERT INTO "django_migrations" VALUES(8,'auth','0002_alter_permission_name_max_length','2026-04-16 12:33:35.954738');
INSERT INTO "django_migrations" VALUES(9,'auth','0003_alter_user_email_max_length','2026-04-16 12:33:35.981615');
INSERT INTO "django_migrations" VALUES(10,'auth','0004_alter_user_username_opts','2026-04-16 12:33:35.998678');
INSERT INTO "django_migrations" VALUES(11,'auth','0005_alter_user_last_login_null','2026-04-16 12:33:36.023487');
INSERT INTO "django_migrations" VALUES(12,'auth','0006_require_contenttypes_0002','2026-04-16 12:33:36.031123');
INSERT INTO "django_migrations" VALUES(13,'auth','0007_alter_validators_add_error_messages','2026-04-16 12:33:36.049762');
INSERT INTO "django_migrations" VALUES(14,'auth','0008_alter_user_username_max_length','2026-04-16 12:33:36.077120');
INSERT INTO "django_migrations" VALUES(15,'auth','0009_alter_user_last_name_max_length','2026-04-16 12:33:36.101488');
INSERT INTO "django_migrations" VALUES(16,'auth','0010_alter_group_name_max_length','2026-04-16 12:33:36.128836');
INSERT INTO "django_migrations" VALUES(17,'auth','0011_update_proxy_permissions','2026-04-16 12:33:36.153012');
INSERT INTO "django_migrations" VALUES(18,'auth','0012_alter_user_first_name_max_length','2026-04-16 12:33:36.191284');
INSERT INTO "django_migrations" VALUES(19,'sessions','0001_initial','2026-04-16 12:33:36.209911');
CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");
CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE INDEX "assistant_statushistory_task_id_e3ada214" ON "assistant_statushistory" ("task_id");
CREATE UNIQUE INDEX "assistant_taskmessage_task_id_channel_7b997f05_uniq" ON "assistant_taskmessage" ("task_id", "channel");
CREATE INDEX "assistant_taskmessage_task_id_66aa3ef5" ON "assistant_taskmessage" ("task_id");
CREATE UNIQUE INDEX "assistant_taskstep_task_id_step_order_deea9d0f_uniq" ON "assistant_taskstep" ("task_id", "step_order");
CREATE INDEX "assistant_taskstep_task_id_e0185197" ON "assistant_taskstep" ("task_id");
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('django_migrations',19);
INSERT INTO "sqlite_sequence" VALUES('django_admin_log',0);
INSERT INTO "sqlite_sequence" VALUES('django_content_type',10);
INSERT INTO "sqlite_sequence" VALUES('auth_permission',40);
INSERT INTO "sqlite_sequence" VALUES('auth_group',0);
INSERT INTO "sqlite_sequence" VALUES('auth_user',0);
INSERT INTO "sqlite_sequence" VALUES('assistant_task',5);
INSERT INTO "sqlite_sequence" VALUES('assistant_taskstep',23);
INSERT INTO "sqlite_sequence" VALUES('assistant_taskmessage',15);
INSERT INTO "sqlite_sequence" VALUES('assistant_statushistory',6);
COMMIT;
