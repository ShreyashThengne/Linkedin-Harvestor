CREATE TABLE name_table(
	name_id serial not null,
	name varchar(100),
	primary key(name_id)
);

CREATE TABLE profile_table(
	p_id serial not null,
	name_id int not null,
	p_link varchar(150),
	website varchar(150),
	im varchar(150),
	phone varchar(13),
	birthday date,
	connections varchar(25),
	followers int,
	about varchar(2000),
	primary key(p_id),
	foreign key (name_id) references name_table(name_id),
	foreign key (birthday) references date_table(dt)
);

CREATE TABLE cert_table(
	cert_sk serial not null,
	cert_org varchar(300),
	cert_name varchar(300),
	primary key(cert_sk)
);

CREATE TABLE skills_table(
	skill_id serial not null,
	skill_name varchar(200),
	primary key(skill_id)
);

CREATE TABLE company_table(
	company_id serial not null,
	company_name varchar(200),
	primary key(company_id)
);

CREATE TABLE role_table(
	role_id serial not null,
	role_name varchar(200),
	primary key(role_id)
);

CREATE TABLE college_table(
	college_id serial not null,
	college_name varchar(300),
	primary key(college_id)
);

CREATE TABLE degree_table(
	degree_id serial not null,
	degree_name varchar(300),
	primary key(degree_id)
);

CREATE TABLE lang_table(
	lang_id serial not null,
	language varchar(100),
	primary key(lang_id)
);

CREATE TABLE award_table(
	award_sk serial not null,
	award_org varchar(300),
	award_name varchar(300),
	primary key(award_sk)
);

CREATE TABLE date_table(
	dt date not null,
	day varchar(20) not null,
	month varchar(20) not null,
	year int not null,
	primary key(dt)
);


-- 
CREATE TABLE p_cert_table(
	p_id_fk int not null,
	cert_sk_fk int not null,
	cert_issued_date date,
	cert_link varchar(300),
	primary key(p_id_fk, cert_sk_fk),
	foreign key (p_id_fk) references profile_table(p_id),
	foreign key (cert_sk_fk) references cert_table(cert_sk)
);

CREATE TABLE p_skills_table(
	p_id_fk int not null,
	skill_id_fk int not null,
	primary key(p_id_fk, skill_id_fk),
	foreign key (p_id_fk) references profile_table(p_id),
	foreign key (skill_id_fk) references skills_table(skill_id)
);

CREATE TABLE p_exp_table(
	p_id_fk int not null,
	company_id_fk int not null,
	role_id_fk int not null,
	job_type varchar(50),
	from_date date,
	to_date date,
	duration int,
	primary key(p_id_fk, company_id_fk, role_id_fk),
	foreign key(p_id_fk) references profile_table(p_id),
	foreign key(company_id_fk) references company_table(company_id),
	foreign key(role_id_fk) references role_table(role_id),
	foreign key(to_date) references date_table(dt),
	foreign key(from_date) references date_table(dt)
);

CREATE TABLE p_edu_table(
	p_id_fk int not null,
	college_id_fk int not null,
	degree_id_fk int not null,
	from_year int,
	to_year int,
	primary key(p_id_fk, college_id_fk, degree_id_fk),
	foreign key(p_id_fk) references profile_table(p_id),
	foreign key(college_id_fk) references college_table(college_id),
	foreign key(degree_id_fk) references degree_table(degree_id)
);

CREATE TABLE p_lang_table(
	p_id_fk int not null,
	lang_id_fk int not null,
	primary key (p_id_fk, lang_id_fk),
	foreign key (p_id_fk) references profile_table(p_id),
	foreign key (lang_id_fk) references lang_table(lang_id)
);

CREATE TABLE p_award_table(
	p_id_fk int not null,
	award_sk_fk int not null,
	award_issued_date date,
	primary key (p_id_fk, award_sk_fk),
	foreign key (p_id_fk) references profile_table(p_id),
	foreign key (award_sk_fk) references award_table(award_sk)
);



