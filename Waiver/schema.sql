drop table if exists seenname;
create table seenname (
       id integer primary key autoincrement,
       name text not null
);

drop table if exists activities;
create table activities (
       id integer primary key autoincrement,
       name text not null,
       activeP boolean not null
);

insert into activities (name,activeP) values ('Tuesday Trail Workouts',1);
insert into activities (name,activeP) values ('Wednesday Morning Crew',1);
insert into activities (name,activeP) values ('Trail Learning Crew',1);
insert into activities (name,activeP) values ('Friday Night Lights',1);
insert into activities (name,activeP) values ('Trail Maintenance',1);
insert into activities (name,activeP) values ('Party!',1);