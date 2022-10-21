insert into hands (hand_label, ts, game_type, bet_limit, num_players, big_blind)
values
('mr big', now(), 'omaha', 'limit', 3, 12.7),
('mr little', now(), 'omaha', 'limit', 3, 12.7);
 
insert into players (hand_id, stack, hole_cards, position, is_hero)
values
((select id from hands limit 1), 300.50, array['3c','2s'], 'UTB+1', true);

insert into streets (hand_id, street_type, board_cards)
values
((select id from hands limit 1), 300.50, array['3c','2s'], 'UTB+1', true);

insert into actions (hand_id, action_order, player_id,action_type,street_id,pot,rake,last_aggression_action_id,num_remaining_players)
values
((select id from hands limit 1),1,player_id,'bet',street_id, 300.50,3, last_agro_id, 2);