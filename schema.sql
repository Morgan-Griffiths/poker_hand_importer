drop table actions;
 
drop table streets;
 
drop table players;
 
drop table hands;
 
drop type game_type;
 
drop type bet_limit;
 
drop type street_type;
 
drop type action_type;
 
create type game_type as enum (
   'omaha',
   'holdem'
);
 
create type bet_limit as enum (
   'limit',
   'no limit',
   'pot limit'
);
 
create type street_type as enum (
   'preflop',
   'flop',
   'turn',
   'river'
);
 
create type action_type as enum (
   'raises',
   'bets',
   'folds',
   'checks',
   'calls',
   'posts'
);
 
create table if not exists hands (
   id serial primary key,
   file_name text not null,
   hand_number int not null,
   ts timestamp not null,
   game_type game_type not null,
   bet_limit bet_limit not null,
   num_players int not null,
   big_blind float not null,
   hero text not null
);
 
create table if not exists players (
   id serial primary key,
   hand_id int not null,
   stack float not null,
   hole_cards varchar(2)[],
   position text not null,
   is_hero boolean not null,
   winnings int not null,
   foreign key (hand_id) references hands (id)
);
 
create table if not exists streets (
   id serial primary key,
   hand_id int not null,
   type street_type not null,
   board_cards varchar(2)[],
   foreign key (hand_id) references hands (id)
);
 
create table if not exists actions (
   id serial primary key,
   hand_id int not null,
   action_order int not null,
   player_id int,
   action_type action_type not null,
   amount float,
   bet_ratio float,
   street_id int not null,
   pot float not null,
   rake float not null,
   last_aggressor_action_id int,
   num_active_players int not null,
   is_blind boolean not null,
   foreign key (hand_id) references hands (id),
   foreign key (player_id) references players (id),
   foreign key (street_id) references streets (id),
   foreign key (last_aggressor_action_id) references actions (id)
);
