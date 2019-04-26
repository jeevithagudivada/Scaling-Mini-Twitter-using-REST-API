INSERT INTO user (username, email, pw_hash)
VALUES
    ('dimpu', 'dimpu@gmail.com', 'pbkdf2:sha256:50000$ZmT3HDGZ$395267f0e03b9785fcdc901cfefb1368b7ca55e9ce59458ddd4490be58691d9b'),
    ('harsha', 'harsha@gmail.com','pbkdf2:sha256:50000$DH2DNYXi$db6b53446b4d4b29f46549889883236bc3f5dd73ac9710227efef391d56d6f84'),
    ('jeevitha', 'jeevitha@gmail.com','pbkdf2:sha256:50000$W03vYT5v$5a91d17fcb35c1d178560491026543a605e6559d9c22d50a0d6510cfbac999c1'),
    ('mounica', 'mounica@gmail.com','pbkdf2:sha256:50000$bmKIiCIo$e61d7b93d5389a9ec03f590686f99d84a1dfc2a3628c9779c9a12e59900d841e'),
    ('harshini', 'harshini@gmail.com','pbkdf2:sha256:50000$gWONg2xk$fe505fffb496131b5259158616c0b7b801257c72b9b37ed47537614dfcc55f2d');

INSERT INTO follower (who_id, whom_id)
VALUES
    ('1', '3'),
    ('5', '4'),
    ('2', '5'),
    ('3', '1'),
	('3', '2'),
    ('2', '4'),
    ('4', '5'),
    ('5', '3');

INSERT INTO message (author_id, text, pub_date)
VALUES
    ('1', 'Life is amazing', '2018-04-19'),
    ('3', 'Hello World', '2018-04-30'),
    ('5', 'Enjoy Every Moment', '2017-11-22'),
    ('2', 'Good Night!', '2018-10-22'),
    ('4', 'All Smiles', '2015-09-09');
