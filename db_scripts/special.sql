insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "size_5"), 1, "Size 1", 1);
insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "size_5"), 2, "Size 2", 2);
insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "size_5"), 4, "Size 3", 3);
insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "size_5"), 8, "Size 4", 4);
insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "sec3"), 1, "Sector 1", 1);
insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "sec3"), 2, "Sector 2", 2);
insert into answer_meanings(question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = "sec3"), 4, "Sector 3", 3);
update questions set question = "Company Size" where question_field = "size_5";
update questions set question = "Sector Type" where question_field = "sec3";
