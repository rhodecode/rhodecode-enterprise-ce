-- MySQL dump 10.13  Distrib 5.5.31, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: rhodecode
-- ------------------------------------------------------
-- Server version	5.5.31-0ubuntu0.12.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cache_invalidation`
--

DROP TABLE IF EXISTS `cache_invalidation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cache_invalidation` (
  `cache_id` int(11) NOT NULL AUTO_INCREMENT,
  `cache_key` varchar(255) DEFAULT NULL,
  `cache_args` varchar(255) DEFAULT NULL,
  `cache_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`cache_id`),
  UNIQUE KEY `cache_id` (`cache_id`),
  UNIQUE KEY `cache_key` (`cache_key`),
  KEY `key_idx` (`cache_key`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cache_invalidation`
--

LOCK TABLES `cache_invalidation` WRITE;
/*!40000 ALTER TABLE `cache_invalidation` DISABLE KEYS */;
INSERT INTO `cache_invalidation` VALUES (1,'1RC/mygr/lol','RC/mygr/lol',0),(2,'1RC/fakeclone','RC/fakeclone',1),(3,'1RC/muay','RC/muay',0),(4,'1BIG/git','BIG/git',1),(5,'1RC/origin-fork','RC/origin-fork',0),(6,'1RC/trololo','RC/trololo',0),(7,'1csa-collins','csa-collins',1),(8,'1csa-harmony','csa-harmony',1),(9,'1RC/Ä…qweqwe','RC/Ä…qweqwe',0),(10,'1rhodecode','rhodecode',0),(11,'1csa-unity','csa-unity',1),(12,'1RC/Å‚Ä™cina','RC/Å‚Ä™cina',0),(13,'1waitress','waitress',1),(14,'1RC/rc2/test2','RC/rc2/test2',1),(15,'1RC/origin-fork-fork','RC/origin-fork-fork',0),(16,'1RC/rc2/test4','RC/rc2/test4',1),(17,'1RC/vcs-git','RC/vcs-git',1),(18,'1rhodecode-extensions','rhodecode-extensions',0),(19,'1rhodecode-cli-gist','rhodecode-cli-gist',0),(20,'1RC/new','RC/new',0),(21,'1csa-aldrin','csa-aldrin',1),(22,'1vcs','vcs',0),(23,'1csa-prometheus','csa-prometheus',1),(24,'1RC/INRC/trololo','RC/INRC/trololo',0),(25,'1RC/empty-git','RC/empty-git',1),(26,'1RC/bin-ops','RC/bin-ops',0),(27,'1csa-salt-states','csa-salt-states',1),(28,'1rhodecode-premium','rhodecode-premium',0),(29,'1RC/qweqwe-fork','RC/qweqwe-fork',0),(30,'1RC/test','RC/test',0),(31,'1remote-salt','remote-salt',1),(32,'1BIG/android','BIG/android',1),(33,'1DOCS','DOCS',1),(34,'1rhodecode-git','rhodecode-git',1),(35,'1RC/fork-remote','RC/fork-remote',0),(36,'1RC/INRC/L2_NEW/lalalal','RC/INRC/L2_NEW/lalalal',0),(37,'1RC/INRC/L2_NEW/L3/repo_test_move','RC/INRC/L2_NEW/L3/repo_test_move',0),(38,'1RC/gogo-fork','RC/gogo-fork',0),(39,'1quest','quest',0),(40,'1RC/foobar','RC/foobar',0),(41,'1csa-hyperion','csa-hyperion',1),(42,'1RC/git-pull-test','RC/git-pull-test',1),(43,'1RC/qweqwe-fork2','RC/qweqwe-fork2',0),(44,'1RC/jap','RC/jap',1),(45,'1RC/hg-repo','RC/hg-repo',0),(46,'1RC/origin','RC/origin',0),(47,'1rhodecode-cli-api','rhodecode-cli-api',0),(48,'1RC/rc2/test3','RC/rc2/test3',1),(49,'1csa-armstrong','csa-armstrong',1),(50,'1pyramidpypi','pyramidpypi',1),(51,'1RC/lol/haha','RC/lol/haha',0),(52,'1csa-io','csa-io',1),(53,'1enc-envelope','enc-envelope',0),(54,'1RC/gogo2','RC/gogo2',0),(55,'1csa-libcloud','csa-libcloud',1),(56,'1RC/git-test','RC/git-test',1),(57,'1RC/rc2/test','RC/rc2/test',0),(58,'1salt','salt',1),(59,'1RC/kiall-nova','RC/kiall-nova',1);
/*!40000 ALTER TABLE `cache_invalidation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `changeset_comments`
--

DROP TABLE IF EXISTS `changeset_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `changeset_comments` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) NOT NULL,
  `revision` varchar(40) DEFAULT NULL,
  `pull_request_id` int(11) DEFAULT NULL,
  `line_no` varchar(10) DEFAULT NULL,
  `hl_lines` varchar(512) DEFAULT NULL,
  `f_path` varchar(1000) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `text` mediumtext NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_at` datetime NOT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `repo_id` (`repo_id`),
  KEY `pull_request_id` (`pull_request_id`),
  KEY `user_id` (`user_id`),
  KEY `cc_revision_idx` (`revision`),
  CONSTRAINT `changeset_comments_ibfk_1` FOREIGN KEY (`repo_id`) REFERENCES `repositories` (`repo_id`),
  CONSTRAINT `changeset_comments_ibfk_2` FOREIGN KEY (`pull_request_id`) REFERENCES `pull_requests` (`pull_request_id`),
  CONSTRAINT `changeset_comments_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `changeset_comments`
--

LOCK TABLES `changeset_comments` WRITE;
/*!40000 ALTER TABLE `changeset_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `changeset_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `changeset_statuses`
--

DROP TABLE IF EXISTS `changeset_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `changeset_statuses` (
  `changeset_status_id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `revision` varchar(40) NOT NULL,
  `status` varchar(128) NOT NULL,
  `changeset_comment_id` int(11) DEFAULT NULL,
  `modified_at` datetime NOT NULL,
  `version` int(11) NOT NULL,
  `pull_request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`changeset_status_id`),
  UNIQUE KEY `repo_id` (`repo_id`,`revision`,`version`),
  KEY `user_id` (`user_id`),
  KEY `changeset_comment_id` (`changeset_comment_id`),
  KEY `pull_request_id` (`pull_request_id`),
  KEY `cs_revision_idx` (`revision`),
  KEY `cs_version_idx` (`version`),
  CONSTRAINT `changeset_statuses_ibfk_1` FOREIGN KEY (`repo_id`) REFERENCES `repositories` (`repo_id`),
  CONSTRAINT `changeset_statuses_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `changeset_statuses_ibfk_3` FOREIGN KEY (`changeset_comment_id`) REFERENCES `changeset_comments` (`comment_id`),
  CONSTRAINT `changeset_statuses_ibfk_4` FOREIGN KEY (`pull_request_id`) REFERENCES `pull_requests` (`pull_request_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `changeset_statuses`
--

LOCK TABLES `changeset_statuses` WRITE;
/*!40000 ALTER TABLE `changeset_statuses` DISABLE KEYS */;
/*!40000 ALTER TABLE `changeset_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `db_migrate_version`
--

DROP TABLE IF EXISTS `db_migrate_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `db_migrate_version` (
  `repository_id` varchar(250) NOT NULL,
  `repository_path` text,
  `version` int(11) DEFAULT NULL,
  PRIMARY KEY (`repository_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `db_migrate_version`
--

LOCK TABLES `db_migrate_version` WRITE;
/*!40000 ALTER TABLE `db_migrate_version` DISABLE KEYS */;
INSERT INTO `db_migrate_version` VALUES ('rhodecode_db_migrations','versions',11);
/*!40000 ALTER TABLE `db_migrate_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(255) NOT NULL,
  `group_parent_id` int(11) DEFAULT NULL,
  `group_description` varchar(10000) DEFAULT NULL,
  `enable_locking` tinyint(1) NOT NULL,
  PRIMARY KEY (`group_id`),
  UNIQUE KEY `group_id` (`group_id`),
  UNIQUE KEY `group_name_2` (`group_name`),
  UNIQUE KEY `group_name` (`group_name`,`group_parent_id`),
  KEY `group_parent_id` (`group_parent_id`),
  CONSTRAINT `groups_ibfk_1` FOREIGN KEY (`group_parent_id`) REFERENCES `groups` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'RC',NULL,'RC group',0),(2,'RC/mygr',1,'RC/mygr group',0),(3,'BIG',NULL,'BIG group',0),(4,'RC/rc2',1,'RC/rc2 group',0),(5,'RC/INRC',1,'RC/INRC group',0),(6,'RC/INRC/L2_NEW',5,'RC/INRC/L2_NEW group',0),(7,'RC/INRC/L2_NEW/L3',6,'RC/INRC/L2_NEW/L3 group',0),(8,'RC/lol',1,'RC/lol group',0);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(512) DEFAULT NULL,
  `body` mediumtext,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime NOT NULL,
  `type` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`notification_id`),
  KEY `created_by` (`created_by`),
  KEY `notification_type_idx` (`type`(255)),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `permission_id` int(11) NOT NULL AUTO_INCREMENT,
  `permission_name` varchar(255) DEFAULT NULL,
  `permission_longname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`permission_id`),
  UNIQUE KEY `permission_id` (`permission_id`),
  KEY `p_perm_name_idx` (`permission_name`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'repository.none','repository.none'),(2,'repository.read','repository.read'),(3,'repository.write','repository.write'),(4,'repository.admin','repository.admin'),(5,'group.none','group.none'),(6,'group.read','group.read'),(7,'group.write','group.write'),(8,'group.admin','group.admin'),(9,'hg.admin','hg.admin'),(10,'hg.create.none','hg.create.none'),(11,'hg.create.repository','hg.create.repository'),(12,'hg.fork.none','hg.fork.none'),(13,'hg.fork.repository','hg.fork.repository'),(14,'hg.register.none','hg.register.none'),(15,'hg.register.manual_activate','hg.register.manual_activate'),(16,'hg.register.auto_activate','hg.register.auto_activate');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pull_request_reviewers`
--

DROP TABLE IF EXISTS `pull_request_reviewers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pull_request_reviewers` (
  `pull_requests_reviewers_id` int(11) NOT NULL AUTO_INCREMENT,
  `pull_request_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`pull_requests_reviewers_id`),
  KEY `pull_request_id` (`pull_request_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `pull_request_reviewers_ibfk_1` FOREIGN KEY (`pull_request_id`) REFERENCES `pull_requests` (`pull_request_id`),
  CONSTRAINT `pull_request_reviewers_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pull_request_reviewers`
--

LOCK TABLES `pull_request_reviewers` WRITE;
/*!40000 ALTER TABLE `pull_request_reviewers` DISABLE KEYS */;
/*!40000 ALTER TABLE `pull_request_reviewers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pull_requests`
--

DROP TABLE IF EXISTS `pull_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pull_requests` (
  `pull_request_id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(256) DEFAULT NULL,
  `description` text,
  `status` varchar(256) NOT NULL,
  `created_on` datetime NOT NULL,
  `updated_on` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `revisions` text,
  `org_repo_id` int(11) NOT NULL,
  `org_ref` varchar(256) NOT NULL,
  `other_repo_id` int(11) NOT NULL,
  `other_ref` varchar(256) NOT NULL,
  PRIMARY KEY (`pull_request_id`),
  KEY `user_id` (`user_id`),
  KEY `org_repo_id` (`org_repo_id`),
  KEY `other_repo_id` (`other_repo_id`),
  CONSTRAINT `pull_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `pull_requests_ibfk_2` FOREIGN KEY (`org_repo_id`) REFERENCES `repositories` (`repo_id`),
  CONSTRAINT `pull_requests_ibfk_3` FOREIGN KEY (`other_repo_id`) REFERENCES `repositories` (`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pull_requests`
--

LOCK TABLES `pull_requests` WRITE;
/*!40000 ALTER TABLE `pull_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `pull_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repo_to_perm`
--

DROP TABLE IF EXISTS `repo_to_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repo_to_perm` (
  `repo_to_perm_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `repository_id` int(11) NOT NULL,
  PRIMARY KEY (`repo_to_perm_id`),
  UNIQUE KEY `user_id` (`user_id`,`repository_id`,`permission_id`),
  UNIQUE KEY `repo_to_perm_id` (`repo_to_perm_id`),
  KEY `permission_id` (`permission_id`),
  KEY `repository_id` (`repository_id`),
  CONSTRAINT `repo_to_perm_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `repo_to_perm_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`),
  CONSTRAINT `repo_to_perm_ibfk_3` FOREIGN KEY (`repository_id`) REFERENCES `repositories` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repo_to_perm`
--

LOCK TABLES `repo_to_perm` WRITE;
/*!40000 ALTER TABLE `repo_to_perm` DISABLE KEYS */;
INSERT INTO `repo_to_perm` VALUES (1,1,2,1),(2,1,2,2),(3,1,2,3),(4,1,2,4),(5,1,2,5),(6,1,2,6),(7,1,2,7),(8,1,2,8),(9,1,2,9),(10,1,2,10),(11,1,2,11),(12,1,2,12),(13,1,2,13),(14,1,2,14),(15,1,2,15),(16,1,2,16),(17,1,2,17),(18,1,2,18),(19,1,2,19),(20,1,2,20),(21,1,2,21),(22,1,2,22),(23,1,2,23),(24,1,2,24),(25,1,2,25),(26,1,2,26),(27,1,2,27),(28,1,2,28),(29,1,2,29),(30,1,2,30),(31,1,2,31),(32,1,2,32),(33,1,2,33),(34,1,2,34),(35,1,2,35),(36,1,2,36),(37,1,2,37),(38,1,2,38),(39,1,2,39),(40,1,2,40),(41,1,2,41),(42,1,2,42),(43,1,2,43),(44,1,2,44),(45,1,2,45),(46,1,2,46),(47,1,2,47),(48,1,2,48),(49,1,2,49),(50,1,2,50),(51,1,2,51),(52,1,2,52),(53,1,2,53),(54,1,2,54),(55,1,2,55),(56,1,2,56),(57,1,2,57),(58,1,2,58),(59,1,2,59);
/*!40000 ALTER TABLE `repo_to_perm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repositories`
--

DROP TABLE IF EXISTS `repositories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repositories` (
  `repo_id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_name` varchar(255) NOT NULL,
  `clone_uri` varchar(255) DEFAULT NULL,
  `repo_type` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `private` tinyint(1) DEFAULT NULL,
  `statistics` tinyint(1) DEFAULT NULL,
  `downloads` tinyint(1) DEFAULT NULL,
  `description` varchar(10000) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `updated_on` datetime DEFAULT NULL,
  `landing_revision` varchar(255) NOT NULL,
  `enable_locking` tinyint(1) NOT NULL,
  `locked` varchar(255) DEFAULT NULL,
  `changeset_cache` blob,
  `fork_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`repo_id`),
  UNIQUE KEY `repo_name` (`repo_name`),
  UNIQUE KEY `repo_id` (`repo_id`),
  UNIQUE KEY `repo_name_2` (`repo_name`),
  KEY `user_id` (`user_id`),
  KEY `fork_id` (`fork_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `repositories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `repositories_ibfk_2` FOREIGN KEY (`fork_id`) REFERENCES `repositories` (`repo_id`),
  CONSTRAINT `repositories_ibfk_3` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repositories`
--

LOCK TABLES `repositories` WRITE;
/*!40000 ALTER TABLE `repositories` DISABLE KEYS */;
INSERT INTO `repositories` VALUES (1,'RC/mygr/lol','http://user@vm/RC/mygr/lol','hg',2,0,0,0,'RC/mygr/lol repository','2013-05-29 14:16:09','2013-05-29 14:16:09','tip',0,NULL,NULL,NULL,2),(2,'RC/fakeclone',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:09','2013-05-09 01:48:00','tip',0,NULL,'{\"raw_id\": \"dfa7d376778d681d1818f41b17706efa6033b407\", \"short_id\": \"dfa7d376778d\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-09T01:48:00\", \"message\": \"fixed\\n\", \"revision\": 293}',NULL,1),(3,'RC/muay',NULL,'hg',2,0,0,0,'RC/muay repository','2013-05-29 14:16:09','2013-05-29 14:16:09','tip',0,NULL,NULL,NULL,1),(4,'BIG/git',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:10','2012-10-21 23:47:54','tip',0,NULL,'{\"raw_id\": \"30f4c66e634760a81ab27a236fe1f2482f6f7856\", \"short_id\": \"30f4c66e6347\", \"author\": \"Junio C Hamano <gitster@pobox.com>\", \"date\": \"2012-10-21T23:47:54\", \"message\": \"What\'s cooking (2012/10 #07)\\n\", \"revision\": 32160}',NULL,3),(5,'RC/origin-fork',NULL,'hg',2,0,0,0,'RC/origin-fork repository','2013-05-29 14:16:11','2013-03-06 20:16:20','tip',0,NULL,'{\"raw_id\": \"f0ce39a6f9edfc6392d4d6137f05bb3871e41780\", \"short_id\": \"f0ce39a6f9ed\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-03-06T20:16:20\", \"message\": \"Edited file via options\\n- fixed 1\\n-f xied 2\\nand so on so on trallalala\", \"revision\": 21}',NULL,1),(6,'RC/trololo',NULL,'hg',2,0,0,0,'RC/trololo repository','2013-05-29 14:16:11','2013-03-28 02:35:50','tip',0,NULL,'{\"raw_id\": \"890d7469abac360637c8cf79f158b170415e1653\", \"short_id\": \"890d7469abac\", \"author\": \"demo user <marcin@maq.io>\", \"date\": \"2013-03-28T02:35:50\", \"message\": \"Added file via RhodeCode\", \"revision\": 0}',NULL,1),(7,'csa-collins',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:11','2013-02-25 17:31:39','tip',0,NULL,'{\"raw_id\": \"8be6a10d645c8dda5f1f331496228118ae872ce8\", \"short_id\": \"8be6a10d645c\", \"author\": \"Bastian Albers <info@bastianalbers.de>\", \"date\": \"2013-02-25T17:31:39\", \"message\": \"Merge branch \'stage\' into stage2\\n\", \"revision\": 2731}',NULL,NULL),(8,'csa-harmony',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:11','2013-05-22 14:49:45','tip',0,NULL,'{\"raw_id\": \"27b59603618b07259ca0db6b00990feeba96930f\", \"short_id\": \"27b59603618b\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-22T14:49:45\", \"message\": \"Added kwargs to setup functions for later optional params\\n\", \"revision\": 339}',NULL,NULL),(9,'RC/Ä…qweqwe',NULL,'hg',2,0,0,0,'RC/Ä…qweqwe repository','2013-05-29 14:16:11','2013-05-29 00:06:28','tip',0,NULL,'{\"raw_id\": \"6c94b338a07134922f042f000f991d47a14bebf9\", \"short_id\": \"6c94b338a071\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-29T00:06:28\", \"message\": \"Edited file \\u0142\\u00f3\\u015b via RhodeCode\", \"revision\": 1}',NULL,1),(10,'rhodecode',NULL,'hg',2,0,0,0,'rhodecode repository','2013-05-29 14:16:11','2013-05-29 12:13:02','tip',0,NULL,'{\"raw_id\": \"424b6c711a7f63680abd1474b66ddf42c0345a16\", \"short_id\": \"424b6c711a7f\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-29T12:13:02\", \"message\": \"allow underscores in usernames. Helps creating special internal users\", \"revision\": 4053}',NULL,NULL),(11,'csa-unity',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:11','2013-04-29 14:38:23','tip',0,NULL,'{\"raw_id\": \"093708759ebf4fd2bb1bdcad61fb611bc32933d3\", \"short_id\": \"093708759ebf\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-29T14:38:23\", \"message\": \"revert to logbook 0.3.0\", \"revision\": 28}',NULL,NULL),(12,'RC/Å‚Ä™cina',NULL,'hg',2,0,0,0,'RC/Å‚Ä™cina repository','2013-05-29 14:16:12','2013-03-06 16:17:49','tip',0,NULL,'{\"raw_id\": \"1ee589bcfa9212c5110ea5c1fe2cc8ff6eaf1303\", \"short_id\": \"1ee589bcfa92\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-03-06T16:17:49\", \"message\": \"Added file via RhodeCode\", \"revision\": 0}',NULL,1),(13,'waitress',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:12','2013-05-28 13:21:35','tip',0,NULL,'{\"raw_id\": \"e5d138ce3f754e6031e7abd76e5f527363fdaf42\", \"short_id\": \"e5d138ce3f75\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-28T13:21:35\", \"message\": \"Added docs and new flag into runner\\n\", \"revision\": 272}',NULL,NULL),(14,'RC/rc2/test2',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:12','2013-03-03 00:29:35','tip',0,NULL,'{\"raw_id\": \"0eb3304fc33d05d328f8627b9ad44dae83f313a2\", \"short_id\": \"0eb3304fc33d\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-03-03T00:29:35\", \"message\": \"Merge branch \'stage\'\\n\\n* stage:\\n  fix requests 1.1 json method\\n  fixed tests\\n  moved tests into package\\n  -bump distribute\\n  update .gitignore\\n  version freeze of libs\\n  remove gevent from IO as dependency\\n  add unity as deps\\n  fully delegate AUTH back to armstrong\\n\", \"revision\": 50}',NULL,4),(15,'RC/origin-fork-fork',NULL,'hg',2,0,0,0,'RC/origin-fork-fork repository','2013-05-29 14:16:12','2013-05-06 23:44:50','tip',0,NULL,'{\"raw_id\": \"6d99e0d4dfcc4a5afa5c138fea2098470634f773\", \"short_id\": \"6d99e0d4dfcc\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-06T23:44:50\", \"message\": \"Issue #17094: Clear stale thread states after fork().\\n\\nNote that this is a potentially disruptive change since it may\\nrelease some system resources which would otherwise remain\\nperpetually alive (e.g. database connections kept in thread-local\\nstorage).\", \"revision\": 25}',NULL,1),(16,'RC/rc2/test4',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:12','2013-03-21 22:55:29','tip',0,NULL,'{\"raw_id\": \"3b6ac7f5e932d4dd13871a0b23d6ca98510d88c2\", \"short_id\": \"3b6ac7f5e932\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-03-21T22:55:29\", \"message\": \"dsadas\", \"revision\": 51}',NULL,4),(17,'RC/vcs-git',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:12','2013-04-26 23:34:15','tip',0,NULL,'{\"raw_id\": \"90da1f69a6c60f7d4d5646ee39ac5f6108bc077c\", \"short_id\": \"90da1f69a6c6\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-26T23:34:15\", \"message\": \"merge with GIT vcs\\n\", \"revision\": 648}',NULL,1),(18,'rhodecode-extensions',NULL,'hg',2,0,0,0,'rhodecode-extensions repository','2013-05-29 14:16:12','2013-02-13 16:50:33','tip',0,NULL,'{\"raw_id\": \"da7e5f7a39d3203ff0b4af5018ac4a80d94ed1d4\", \"short_id\": \"da7e5f7a39d3\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-02-13T16:50:33\", \"message\": \"Linkify hipchat messages\", \"revision\": 2}',NULL,NULL),(19,'rhodecode-cli-gist',NULL,'hg',2,0,0,0,'rhodecode-cli-gist repository','2013-05-29 14:16:12','2013-05-29 14:16:12','tip',0,NULL,NULL,NULL,NULL),(20,'RC/new',NULL,'hg',2,0,0,0,'RC/new repository','2013-05-29 14:16:12','2013-04-17 13:02:59','tip',0,NULL,'{\"raw_id\": \"93192e03a3552b8da4fee40e001c60304723bb42\", \"short_id\": \"93192e03a355\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-17T13:02:59\", \"message\": \"rename\", \"revision\": 1}',NULL,1),(21,'csa-aldrin',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:12','2013-05-02 23:47:52','tip',0,NULL,'{\"raw_id\": \"67ee9e830c225921ec15974ac1dfde17a930e2fb\", \"short_id\": \"67ee9e830c22\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-02T23:47:52\", \"message\": \"Merge branch \'stage\'\\n\\n* stage:\\n  moved gevent into out internal server\\n  stupid assholes in gevent should learn how to package...\\n  fixed gevent dependency link\\n  added separate call for session validation\\n\", \"revision\": 293}',NULL,NULL),(22,'vcs',NULL,'hg',2,0,0,0,'vcs repository','2013-05-29 14:16:13','2013-05-09 00:28:54','tip',0,NULL,'{\"raw_id\": \"6fba59f9f7806a545a0e5ebac936991828436260\", \"short_id\": \"6fba59f9f780\", \"author\": \"Lukasz Balcerzak <lukaszbalcerzak@gmail.com>\", \"date\": \"2013-05-09T00:28:54\", \"message\": \"Merge pull request #117 from niedbalski/master\\n\\nKeyError: \'all\'\", \"revision\": 707}',NULL,NULL),(23,'csa-prometheus',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:13','2013-04-29 14:37:43','tip',0,NULL,'{\"raw_id\": \"a719bd82d25e7411fdb7979c12c083f59a206a6c\", \"short_id\": \"a719bd82d25e\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-29T14:37:43\", \"message\": \"revert logbook to 0.3.0\", \"revision\": 79}',NULL,NULL),(24,'RC/INRC/trololo',NULL,'hg',2,0,0,0,'RC/INRC/trololo repository','2013-05-29 14:16:13','2013-05-29 14:16:13','tip',0,NULL,NULL,NULL,5),(25,'RC/empty-git',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:13','2013-05-29 14:16:13','tip',0,NULL,NULL,NULL,1),(26,'RC/bin-ops',NULL,'hg',2,0,0,0,'RC/bin-ops repository','2013-05-29 14:16:13','2013-05-12 12:39:34','tip',0,NULL,'{\"raw_id\": \"4231762d8c1aaca5be3db15991071236c32e7654\", \"short_id\": \"4231762d8c1a\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-12T12:39:34\", \"message\": \"Edited file file1 via RhodeCode\", \"revision\": 23}',NULL,1),(27,'csa-salt-states',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:13','2013-05-06 14:48:48','tip',0,NULL,'{\"raw_id\": \"0c20dc72baeedc3ce840c611174c7e1cd3b04919\", \"short_id\": \"0c20dc72baee\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-06T14:48:48\", \"message\": \"increase sampling of CPU time to 0.5s for more realistic data.\", \"revision\": 71}',NULL,NULL),(28,'rhodecode-premium',NULL,'hg',2,0,0,0,'rhodecode-premium repository','2013-05-29 14:16:13','2013-03-21 22:58:11','tip',0,NULL,'{\"raw_id\": \"ded35bf017f16bcad6611c7ffe3b1b1c10942f50\", \"short_id\": \"ded35bf017f1\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-03-21T22:58:11\", \"message\": \"version bump to 1.5.4p2\", \"revision\": 3674}',NULL,NULL),(29,'RC/qweqwe-fork',NULL,'hg',2,0,0,0,'RC/qweqwe-fork repository','2013-05-29 14:16:13','2013-05-29 14:16:13','tip',0,NULL,NULL,NULL,1),(30,'RC/test',NULL,'hg',2,0,0,0,'RC/test repository','2013-05-29 14:16:13','2013-01-30 22:56:03','tip',0,NULL,'{\"raw_id\": \"e5025e316d9acb39e5f861c494240be4f5d56de6\", \"short_id\": \"e5025e316d9a\", \"author\": \"RhodeCode Admin <marcin@maq.io>\", \"date\": \"2013-01-30T22:56:03\", \"message\": \"<script>alert(\'xss2\');</script>  fixes #700\", \"revision\": 2}',NULL,1),(31,'remote-salt',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:13','2012-10-14 22:04:05','tip',0,NULL,'{\"raw_id\": \"d661dc72492e66cab7a647dcb5652009067aa8cd\", \"short_id\": \"d661dc72492e\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2012-10-14T22:04:05\", \"message\": \"Logging\\nOn-the-fly msg encryption using googles keyCzar lib\", \"revision\": 3}',NULL,NULL),(32,'BIG/android',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:13','2012-06-17 00:44:46','tip',0,NULL,'{\"raw_id\": \"e86b147e4b6908a7c5ab0963d77fb0867679b1ee\", \"short_id\": \"e86b147e4b69\", \"author\": \"Bernhard Rosenkraenzer <Bernhard.Rosenkranzer@linaro.org>\", \"date\": \"2012-06-17T00:44:46\", \"message\": \"panda: Backport HDMI vs. DVI patch from kernel/panda.git\\n\\nThis patch allows switching the primary display output device.\\n\\nChange-Id: I6e30e87bbc7aa72b5acc6e6c4ed34019835e6524\\nSigned-off-by: Bernhard Rosenkraenzer <Bernhard.Rosenkranzer@linaro.org>\\n\", \"revision\": 294896}',NULL,3),(33,'DOCS',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:24','2013-04-25 16:45:59','tip',0,NULL,'{\"raw_id\": \"1e4a728ee7a6aa88be11260d6479a446eb865de3\", \"short_id\": \"1e4a728ee7a6\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-25T16:45:59\", \"message\": \"sync docs with armstrong\", \"revision\": 15}',NULL,NULL),(34,'rhodecode-git',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:24','2013-01-04 00:24:22','tip',0,NULL,'{\"raw_id\": \"629f1538ad4800ff05113516f6a933e2b243f205\", \"short_id\": \"629f1538ad48\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-01-04T00:24:22\", \"message\": \"nicer representation of list of rescanned repositories\\n\\n--HG--\\nbranch : beta\\n\", \"revision\": 3142}',NULL,NULL),(35,'RC/fork-remote',NULL,'hg',2,0,0,0,'RC/fork-remote repository','2013-05-29 14:16:24','2013-03-10 22:47:24','tip',0,NULL,'{\"raw_id\": \"60555484a0a0d6e525e9d7ab1b1dce5ab9eb9487\", \"short_id\": \"60555484a0a0\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-03-10T22:47:24\", \"message\": \"aaa\", \"revision\": 26}',NULL,1),(36,'RC/INRC/L2_NEW/lalalal',NULL,'hg',2,0,0,0,'RC/INRC/L2_NEW/lalalal repository','2013-05-29 14:16:24','2013-05-29 14:16:24','tip',0,NULL,NULL,NULL,6),(37,'RC/INRC/L2_NEW/L3/repo_test_move',NULL,'hg',2,0,0,0,'RC/INRC/L2_NEW/L3/repo_test_move repository','2013-05-29 14:16:25','2013-05-29 14:16:25','tip',0,NULL,NULL,NULL,7),(38,'RC/gogo-fork',NULL,'hg',2,0,0,0,'RC/gogo-fork repository','2013-05-29 14:16:25','2013-05-28 21:33:55','tip',0,NULL,'{\"raw_id\": \"d72044a6e192f89de3f2b723557942eecb420308\", \"short_id\": \"d72044a6e192\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-28T21:33:55\", \"message\": \"Added file via RhodeCode\", \"revision\": 0}',NULL,1),(39,'quest',NULL,'hg',2,0,0,0,'quest repository','2013-05-29 14:16:25','2013-03-04 23:01:40','tip',0,NULL,'{\"raw_id\": \"54b01cfdea25bf41cd8e9a184c5852c5d48d864c\", \"short_id\": \"54b01cfdea25\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-03-04T23:01:40\", \"message\": \"template and version 0.0.1\", \"revision\": 41}',NULL,NULL),(40,'RC/foobar',NULL,'hg',2,0,0,0,'RC/foobar repository','2013-05-29 14:16:25','2013-04-15 21:34:57','tip',0,NULL,'{\"raw_id\": \"c17dc3c566952813e84037dfd62a4755ed3c912c\", \"short_id\": \"c17dc3c56695\", \"author\": \"Mirek Kott <marcin@python-blog.com>\", \"date\": \"2013-04-15T21:34:57\", \"message\": \"Edited file lol.rst via RhodeCode\", \"revision\": 1}',NULL,1),(41,'csa-hyperion',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:25','2013-05-20 21:58:28','tip',0,NULL,'{\"raw_id\": \"252c926d10702e6ef7c2456f2fc23892808e53a0\", \"short_id\": \"252c926d1070\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-20T21:58:28\", \"message\": \"fixes for new code\\n\", \"revision\": 57}',NULL,NULL),(42,'RC/git-pull-test',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:25','2013-05-20 13:03:02','tip',0,NULL,'{\"raw_id\": \"b2cf1136f09fa61df90469b43310615984bc7d55\", \"short_id\": \"b2cf1136f09f\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-20T13:03:02\", \"message\": \"added\\n\", \"revision\": 13}',NULL,1),(43,'RC/qweqwe-fork2',NULL,'hg',2,0,0,0,'RC/qweqwe-fork2 repository','2013-05-29 14:16:25','2013-05-29 14:16:25','tip',0,NULL,NULL,NULL,1),(44,'RC/jap',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:25','2013-04-24 11:15:30','tip',0,NULL,'{\"raw_id\": \"2f62ce22453a67eefd6fab1d4e053520e8debdf6\", \"short_id\": \"2f62ce22453a\", \"author\": \"Demo User <demo@rhodecode.org>\", \"date\": \"2013-04-24T11:15:30\", \"message\": \"\\u30d5\\u30a1\\u30a4\\u30eb\\u8ffd\\u52a0\", \"revision\": 5}',NULL,1),(45,'RC/hg-repo',NULL,'hg',2,0,0,0,'RC/hg-repo repository','2013-05-29 14:16:25','2013-05-08 22:54:45','tip',0,NULL,'{\"raw_id\": \"d63d40e8b0685af6db5f2cf7700e80216af5c739\", \"short_id\": \"d63d40e8b068\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-08T22:54:45\", \"message\": \"Edited file haha via RhodeCode\", \"revision\": 25}',NULL,1),(46,'RC/origin',NULL,'hg',2,0,0,0,'RC/origin repository','2013-05-29 14:16:25','2013-04-05 13:05:02','tip',0,NULL,'{\"raw_id\": \"5fbf2f0eada43bc33a94e483503335d8f6757093\", \"short_id\": \"5fbf2f0eada4\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-05T13:05:02\", \"message\": \"fixed\", \"revision\": 29}',NULL,1),(47,'rhodecode-cli-api',NULL,'hg',2,0,0,0,'rhodecode-cli-api repository','2013-05-29 14:16:25','2013-05-29 14:16:25','tip',0,NULL,NULL,NULL,NULL),(48,'RC/rc2/test3',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:25','2013-03-03 00:29:35','tip',0,NULL,'{\"raw_id\": \"0eb3304fc33d05d328f8627b9ad44dae83f313a2\", \"short_id\": \"0eb3304fc33d\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-03-03T00:29:35\", \"message\": \"Merge branch \'stage\'\\n\\n* stage:\\n  fix requests 1.1 json method\\n  fixed tests\\n  moved tests into package\\n  -bump distribute\\n  update .gitignore\\n  version freeze of libs\\n  remove gevent from IO as dependency\\n  add unity as deps\\n  fully delegate AUTH back to armstrong\\n\", \"revision\": 50}',NULL,4),(49,'csa-armstrong',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:26','2013-05-22 18:10:20','tip',0,NULL,'{\"raw_id\": \"60ffa2018fa120c97c0c5fcab93ecd82e2c3a691\", \"short_id\": \"60ffa2018fa1\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-22T18:10:20\", \"message\": \"fix actual progress increase in salt calls\\n\", \"revision\": 1140}',NULL,NULL),(50,'pyramidpypi',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:26','2013-04-25 16:34:48','tip',0,NULL,'{\"raw_id\": \"ed9aceffada3ef38509c5d7010b016ba45e82944\", \"short_id\": \"ed9aceffada3\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-25T16:34:48\", \"message\": \"version bump\", \"revision\": 28}',NULL,NULL),(51,'RC/lol/haha',NULL,'hg',2,0,0,0,'RC/lol/haha repository','2013-05-29 14:16:26','2013-05-29 14:16:26','tip',0,NULL,NULL,NULL,8),(52,'csa-io',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:26','2013-05-02 22:52:54','tip',0,NULL,'{\"raw_id\": \"bd0ef71fcfd088a82b8627e60aaa1f2020ed33ba\", \"short_id\": \"bd0ef71fcfd0\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-05-02T22:52:54\", \"message\": \"Merge branch \'stage\'\\n\\n* stage:\\n  Use ext_json instead of plain simplejson serializer\\n  log errors on restfull json parsers/decoders\\n  fixed some serialization problems\\n  version bump\\n  Repository revisions API\\n  mercurial version bump\\n  Bump VCS version to 0.4.0 and move it to code.appzonaut.com\\n  fix logging on changes json module in requests 1.X\\n\", \"revision\": 59}',NULL,NULL),(53,'enc-envelope',NULL,'hg',2,0,0,0,'enc-envelope repository','2013-05-29 14:16:26','2013-03-07 15:37:40','tip',0,NULL,'{\"raw_id\": \"810066f835d6c082950fc7828ded50b9b8d9c229\", \"short_id\": \"810066f835d6\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-03-07T15:37:40\", \"message\": \"show more detailed info about wrong stream\", \"revision\": 5}',NULL,NULL),(54,'RC/gogo2',NULL,'hg',2,0,0,0,'RC/gogo2 repository','2013-05-29 14:16:26','2013-05-28 21:33:39','tip',0,NULL,'{\"raw_id\": \"07f1002bc22aff4231f7c94b54715547c29c37c6\", \"short_id\": \"07f1002bc22a\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-28T21:33:39\", \"message\": \"Added file via RhodeCode\", \"revision\": 0}',NULL,1),(55,'csa-libcloud',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:27','2013-04-17 16:42:42','tip',0,NULL,'{\"raw_id\": \"a2fa551633ce3697ac63a935aa71f1e7b80222ae\", \"short_id\": \"a2fa551633ce\", \"author\": \"Marcin Kuzminski <marcin@python-works.com>\", \"date\": \"2013-04-17T16:42:42\", \"message\": \"filter only listeners Brightbox can process\", \"revision\": 1895}',NULL,NULL),(56,'RC/git-test',NULL,'git',2,0,0,0,'Unnamed repository','2013-05-29 14:16:27','2013-05-29 00:10:16','tip',0,NULL,'{\"raw_id\": \"c0d94361073eaf60106b60af628949a1bad45f2d\", \"short_id\": \"c0d94361073e\", \"author\": \"RhodeCode Admin <marcin@python-blog.com>\", \"date\": \"2013-05-29T00:10:16\", \"message\": \"Edited file \\u0142\\u00f3\\u015b via RhodeCode\", \"revision\": 11}',NULL,1),(57,'RC/rc2/test',NULL,'hg',2,0,0,0,'RC/rc2/test repository','2013-05-29 14:16:27','2013-05-29 14:16:27','tip',0,NULL,NULL,NULL,4),(58,'salt',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:27','2012-10-15 05:20:58','tip',0,NULL,'{\"raw_id\": \"bd44832230fc19eb80fe49ef01badb477ef8ca6c\", \"short_id\": \"bd44832230fc\", \"author\": \"Thomas S Hatch <thatch45@gmail.com>\", \"date\": \"2012-10-15T05:20:58\", \"message\": \"Merge pull request #2244 from FireHost/toplevel_wmi_import\\n\\nToplevel wmi import\", \"revision\": 6957}',NULL,NULL),(59,'RC/kiall-nova',NULL,'git',2,0,0,0,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:16:27','2012-10-23 10:22:06','tip',0,NULL,'{\"raw_id\": \"a0fcd1248071ad66b610eac4903adf36b314390b\", \"short_id\": \"a0fcd1248071\", \"author\": \"Jenkins <jenkins@review.openstack.org>\", \"date\": \"2012-10-23T10:22:06\", \"message\": \"Merge \\\"Fix nova-volume-usage-audit\\\"\", \"revision\": 17253}',NULL,1);
/*!40000 ALTER TABLE `repositories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repositories_fields`
--

DROP TABLE IF EXISTS `repositories_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repositories_fields` (
  `repo_field_id` int(11) NOT NULL AUTO_INCREMENT,
  `repository_id` int(11) NOT NULL,
  `field_key` varchar(250) DEFAULT NULL,
  `field_label` varchar(1024) NOT NULL,
  `field_value` varchar(10000) NOT NULL,
  `field_desc` varchar(1024) NOT NULL,
  `field_type` varchar(256) NOT NULL,
  `created_on` datetime NOT NULL,
  PRIMARY KEY (`repo_field_id`),
  UNIQUE KEY `repo_field_id` (`repo_field_id`),
  UNIQUE KEY `repository_id` (`repository_id`,`field_key`),
  CONSTRAINT `repositories_fields_ibfk_1` FOREIGN KEY (`repository_id`) REFERENCES `repositories` (`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repositories_fields`
--

LOCK TABLES `repositories_fields` WRITE;
/*!40000 ALTER TABLE `repositories_fields` DISABLE KEYS */;
/*!40000 ALTER TABLE `repositories_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rhodecode_settings`
--

DROP TABLE IF EXISTS `rhodecode_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rhodecode_settings` (
  `app_settings_id` int(11) NOT NULL AUTO_INCREMENT,
  `app_settings_name` varchar(255) DEFAULT NULL,
  `app_settings_value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`app_settings_id`),
  UNIQUE KEY `app_settings_id` (`app_settings_id`),
  UNIQUE KEY `app_settings_name` (`app_settings_name`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rhodecode_settings`
--

LOCK TABLES `rhodecode_settings` WRITE;
/*!40000 ALTER TABLE `rhodecode_settings` DISABLE KEYS */;
INSERT INTO `rhodecode_settings` VALUES (1,'realm','RhodeCode authentication'),(2,'title','RhodeCode'),(3,'ga_code',''),(4,'show_public_icon','True'),(5,'show_private_icon','True'),(6,'stylify_metatags','False'),(7,'ldap_active','false'),(8,'ldap_host',''),(9,'ldap_port','389'),(10,'ldap_tls_kind','PLAIN'),(11,'ldap_tls_reqcert',''),(12,'ldap_dn_user',''),(13,'ldap_dn_pass',''),(14,'ldap_base_dn',''),(15,'ldap_filter',''),(16,'ldap_search_scope',''),(17,'ldap_attr_login',''),(18,'ldap_attr_firstname',''),(19,'ldap_attr_lastname',''),(20,'ldap_attr_email',''),(21,'default_repo_enable_locking','False'),(22,'default_repo_enable_downloads','False'),(23,'default_repo_enable_statistics','False'),(24,'default_repo_private','False'),(25,'default_repo_type','hg');
/*!40000 ALTER TABLE `rhodecode_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rhodecode_ui`
--

DROP TABLE IF EXISTS `rhodecode_ui`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rhodecode_ui` (
  `ui_id` int(11) NOT NULL AUTO_INCREMENT,
  `ui_section` varchar(255) DEFAULT NULL,
  `ui_key` varchar(255) DEFAULT NULL,
  `ui_value` varchar(255) DEFAULT NULL,
  `ui_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ui_id`),
  UNIQUE KEY `ui_id` (`ui_id`),
  UNIQUE KEY `ui_key` (`ui_key`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rhodecode_ui`
--

LOCK TABLES `rhodecode_ui` WRITE;
/*!40000 ALTER TABLE `rhodecode_ui` DISABLE KEYS */;
INSERT INTO `rhodecode_ui` VALUES (1,'hooks','changegroup.update','hg update >&2',0),(2,'hooks','changegroup.repo_size','python:rhodecode.lib.hooks.repo_size',1),(3,'hooks','changegroup.push_logger','python:rhodecode.lib.hooks.log_push_action',1),(4,'hooks','prechangegroup.pre_push','python:rhodecode.lib.hooks.pre_push',1),(5,'hooks','outgoing.pull_logger','python:rhodecode.lib.hooks.log_pull_action',1),(6,'hooks','preoutgoing.pre_pull','python:rhodecode.lib.hooks.pre_pull',1),(7,'extensions','largefiles','',1),(8,'extensions','hgsubversion','',0),(9,'extensions','hggit','',0),(10,'web','push_ssl','false',1),(11,'web','allow_archive','gz zip bz2',1),(12,'web','allow_push','*',1),(13,'web','baseurl','/',1),(14,'paths','/','/mnt/hgfs/workspace-python',1);
/*!40000 ALTER TABLE `rhodecode_ui` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statistics`
--

DROP TABLE IF EXISTS `statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statistics` (
  `stat_id` int(11) NOT NULL AUTO_INCREMENT,
  `repository_id` int(11) NOT NULL,
  `stat_on_revision` int(11) NOT NULL,
  `commit_activity` mediumblob NOT NULL,
  `commit_activity_combined` blob NOT NULL,
  `languages` mediumblob NOT NULL,
  PRIMARY KEY (`stat_id`),
  UNIQUE KEY `repository_id` (`repository_id`),
  UNIQUE KEY `stat_id` (`stat_id`),
  UNIQUE KEY `repository_id_2` (`repository_id`),
  CONSTRAINT `statistics_ibfk_1` FOREIGN KEY (`repository_id`) REFERENCES `repositories` (`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statistics`
--

LOCK TABLES `statistics` WRITE;
/*!40000 ALTER TABLE `statistics` DISABLE KEYS */;
/*!40000 ALTER TABLE `statistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_email_map`
--

DROP TABLE IF EXISTS `user_email_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_email_map` (
  `email_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`email_id`),
  UNIQUE KEY `email_id` (`email_id`),
  UNIQUE KEY `email` (`email`),
  KEY `user_id` (`user_id`),
  KEY `uem_email_idx` (`email`),
  CONSTRAINT `user_email_map_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_email_map`
--

LOCK TABLES `user_email_map` WRITE;
/*!40000 ALTER TABLE `user_email_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_email_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_followings`
--

DROP TABLE IF EXISTS `user_followings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_followings` (
  `user_following_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `follows_repository_id` int(11) DEFAULT NULL,
  `follows_user_id` int(11) DEFAULT NULL,
  `follows_from` datetime DEFAULT NULL,
  PRIMARY KEY (`user_following_id`),
  UNIQUE KEY `user_following_id` (`user_following_id`),
  UNIQUE KEY `user_id` (`user_id`,`follows_repository_id`),
  UNIQUE KEY `user_id_2` (`user_id`,`follows_user_id`),
  KEY `follows_repository_id` (`follows_repository_id`),
  KEY `follows_user_id` (`follows_user_id`),
  CONSTRAINT `user_followings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `user_followings_ibfk_2` FOREIGN KEY (`follows_repository_id`) REFERENCES `repositories` (`repo_id`),
  CONSTRAINT `user_followings_ibfk_3` FOREIGN KEY (`follows_user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_followings`
--

LOCK TABLES `user_followings` WRITE;
/*!40000 ALTER TABLE `user_followings` DISABLE KEYS */;
INSERT INTO `user_followings` VALUES (1,2,1,NULL,'2013-05-29 14:16:09'),(2,2,2,NULL,'2013-05-29 14:16:09'),(3,2,3,NULL,'2013-05-29 14:16:10'),(4,2,4,NULL,'2013-05-29 14:16:10'),(5,2,5,NULL,'2013-05-29 14:16:11'),(6,2,6,NULL,'2013-05-29 14:16:11'),(7,2,7,NULL,'2013-05-29 14:16:11'),(8,2,8,NULL,'2013-05-29 14:16:11'),(9,2,9,NULL,'2013-05-29 14:16:11'),(10,2,10,NULL,'2013-05-29 14:16:11'),(11,2,11,NULL,'2013-05-29 14:16:11'),(12,2,12,NULL,'2013-05-29 14:16:12'),(13,2,13,NULL,'2013-05-29 14:16:12'),(14,2,14,NULL,'2013-05-29 14:16:12'),(15,2,15,NULL,'2013-05-29 14:16:12'),(16,2,16,NULL,'2013-05-29 14:16:12'),(17,2,17,NULL,'2013-05-29 14:16:12'),(18,2,18,NULL,'2013-05-29 14:16:12'),(19,2,19,NULL,'2013-05-29 14:16:12'),(20,2,20,NULL,'2013-05-29 14:16:12'),(21,2,21,NULL,'2013-05-29 14:16:12'),(22,2,22,NULL,'2013-05-29 14:16:13'),(23,2,23,NULL,'2013-05-29 14:16:13'),(24,2,24,NULL,'2013-05-29 14:16:13'),(25,2,25,NULL,'2013-05-29 14:16:13'),(26,2,26,NULL,'2013-05-29 14:16:13'),(27,2,27,NULL,'2013-05-29 14:16:13'),(28,2,28,NULL,'2013-05-29 14:16:13'),(29,2,29,NULL,'2013-05-29 14:16:13'),(30,2,30,NULL,'2013-05-29 14:16:13'),(31,2,31,NULL,'2013-05-29 14:16:13'),(32,2,32,NULL,'2013-05-29 14:16:13'),(33,2,33,NULL,'2013-05-29 14:16:24'),(34,2,34,NULL,'2013-05-29 14:16:24'),(35,2,35,NULL,'2013-05-29 14:16:24'),(36,2,36,NULL,'2013-05-29 14:16:24'),(37,2,37,NULL,'2013-05-29 14:16:25'),(38,2,38,NULL,'2013-05-29 14:16:25'),(39,2,39,NULL,'2013-05-29 14:16:25'),(40,2,40,NULL,'2013-05-29 14:16:25'),(41,2,41,NULL,'2013-05-29 14:16:25'),(42,2,42,NULL,'2013-05-29 14:16:25'),(43,2,43,NULL,'2013-05-29 14:16:25'),(44,2,44,NULL,'2013-05-29 14:16:25'),(45,2,45,NULL,'2013-05-29 14:16:25'),(46,2,46,NULL,'2013-05-29 14:16:25'),(47,2,47,NULL,'2013-05-29 14:16:25'),(48,2,48,NULL,'2013-05-29 14:16:25'),(49,2,49,NULL,'2013-05-29 14:16:26'),(50,2,50,NULL,'2013-05-29 14:16:26'),(51,2,51,NULL,'2013-05-29 14:16:26'),(52,2,52,NULL,'2013-05-29 14:16:26'),(53,2,53,NULL,'2013-05-29 14:16:26'),(54,2,54,NULL,'2013-05-29 14:16:26'),(55,2,55,NULL,'2013-05-29 14:16:27'),(56,2,56,NULL,'2013-05-29 14:16:27'),(57,2,57,NULL,'2013-05-29 14:16:27'),(58,2,58,NULL,'2013-05-29 14:16:27'),(59,2,59,NULL,'2013-05-29 14:16:27');
/*!40000 ALTER TABLE `user_followings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_ip_map`
--

DROP TABLE IF EXISTS `user_ip_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_ip_map` (
  `ip_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `ip_addr` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ip_id`),
  UNIQUE KEY `ip_id` (`ip_id`),
  UNIQUE KEY `user_id` (`user_id`,`ip_addr`),
  CONSTRAINT `user_ip_map_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_ip_map`
--

LOCK TABLES `user_ip_map` WRITE;
/*!40000 ALTER TABLE `user_ip_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_ip_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_logs`
--

DROP TABLE IF EXISTS `user_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_logs` (
  `user_log_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `repository_id` int(11) DEFAULT NULL,
  `repository_name` varchar(255) DEFAULT NULL,
  `user_ip` varchar(255) DEFAULT NULL,
  `action` mediumtext,
  `action_date` datetime DEFAULT NULL,
  PRIMARY KEY (`user_log_id`),
  UNIQUE KEY `user_log_id` (`user_log_id`),
  KEY `user_id` (`user_id`),
  KEY `repository_id` (`repository_id`),
  CONSTRAINT `user_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `user_logs_ibfk_2` FOREIGN KEY (`repository_id`) REFERENCES `repositories` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_logs`
--

LOCK TABLES `user_logs` WRITE;
/*!40000 ALTER TABLE `user_logs` DISABLE KEYS */;
INSERT INTO `user_logs` VALUES (1,2,'marcink',1,'RC/mygr/lol','','started_following_repo','2013-05-29 14:16:09'),(2,2,'marcink',2,'RC/fakeclone','','started_following_repo','2013-05-29 14:16:09'),(3,2,'marcink',3,'RC/muay','','started_following_repo','2013-05-29 14:16:09'),(4,2,'marcink',4,'BIG/git','','started_following_repo','2013-05-29 14:16:10'),(5,2,'marcink',5,'RC/origin-fork','','started_following_repo','2013-05-29 14:16:11'),(6,2,'marcink',6,'RC/trololo','','started_following_repo','2013-05-29 14:16:11'),(7,2,'marcink',7,'csa-collins','','started_following_repo','2013-05-29 14:16:11'),(8,2,'marcink',8,'csa-harmony','','started_following_repo','2013-05-29 14:16:11'),(9,2,'marcink',9,'RC/Ä…qweqwe','','started_following_repo','2013-05-29 14:16:11'),(10,2,'marcink',10,'rhodecode','','started_following_repo','2013-05-29 14:16:11'),(11,2,'marcink',11,'csa-unity','','started_following_repo','2013-05-29 14:16:11'),(12,2,'marcink',12,'RC/Å‚Ä™cina','','started_following_repo','2013-05-29 14:16:12'),(13,2,'marcink',13,'waitress','','started_following_repo','2013-05-29 14:16:12'),(14,2,'marcink',14,'RC/rc2/test2','','started_following_repo','2013-05-29 14:16:12'),(15,2,'marcink',15,'RC/origin-fork-fork','','started_following_repo','2013-05-29 14:16:12'),(16,2,'marcink',16,'RC/rc2/test4','','started_following_repo','2013-05-29 14:16:12'),(17,2,'marcink',17,'RC/vcs-git','','started_following_repo','2013-05-29 14:16:12'),(18,2,'marcink',18,'rhodecode-extensions','','started_following_repo','2013-05-29 14:16:12'),(19,2,'marcink',19,'rhodecode-cli-gist','','started_following_repo','2013-05-29 14:16:12'),(20,2,'marcink',20,'RC/new','','started_following_repo','2013-05-29 14:16:12'),(21,2,'marcink',21,'csa-aldrin','','started_following_repo','2013-05-29 14:16:12'),(22,2,'marcink',22,'vcs','','started_following_repo','2013-05-29 14:16:13'),(23,2,'marcink',23,'csa-prometheus','','started_following_repo','2013-05-29 14:16:13'),(24,2,'marcink',24,'RC/INRC/trololo','','started_following_repo','2013-05-29 14:16:13'),(25,2,'marcink',25,'RC/empty-git','','started_following_repo','2013-05-29 14:16:13'),(26,2,'marcink',26,'RC/bin-ops','','started_following_repo','2013-05-29 14:16:13'),(27,2,'marcink',27,'csa-salt-states','','started_following_repo','2013-05-29 14:16:13'),(28,2,'marcink',28,'rhodecode-premium','','started_following_repo','2013-05-29 14:16:13'),(29,2,'marcink',29,'RC/qweqwe-fork','','started_following_repo','2013-05-29 14:16:13'),(30,2,'marcink',30,'RC/test','','started_following_repo','2013-05-29 14:16:13'),(31,2,'marcink',31,'remote-salt','','started_following_repo','2013-05-29 14:16:13'),(32,2,'marcink',32,'BIG/android','','started_following_repo','2013-05-29 14:16:13'),(33,2,'marcink',33,'DOCS','','started_following_repo','2013-05-29 14:16:24'),(34,2,'marcink',34,'rhodecode-git','','started_following_repo','2013-05-29 14:16:24'),(35,2,'marcink',35,'RC/fork-remote','','started_following_repo','2013-05-29 14:16:24'),(36,2,'marcink',36,'RC/INRC/L2_NEW/lalalal','','started_following_repo','2013-05-29 14:16:24'),(37,2,'marcink',37,'RC/INRC/L2_NEW/L3/repo_test_move','','started_following_repo','2013-05-29 14:16:25'),(38,2,'marcink',38,'RC/gogo-fork','','started_following_repo','2013-05-29 14:16:25'),(39,2,'marcink',39,'quest','','started_following_repo','2013-05-29 14:16:25'),(40,2,'marcink',40,'RC/foobar','','started_following_repo','2013-05-29 14:16:25'),(41,2,'marcink',41,'csa-hyperion','','started_following_repo','2013-05-29 14:16:25'),(42,2,'marcink',42,'RC/git-pull-test','','started_following_repo','2013-05-29 14:16:25'),(43,2,'marcink',43,'RC/qweqwe-fork2','','started_following_repo','2013-05-29 14:16:25'),(44,2,'marcink',44,'RC/jap','','started_following_repo','2013-05-29 14:16:25'),(45,2,'marcink',45,'RC/hg-repo','','started_following_repo','2013-05-29 14:16:25'),(46,2,'marcink',46,'RC/origin','','started_following_repo','2013-05-29 14:16:25'),(47,2,'marcink',47,'rhodecode-cli-api','','started_following_repo','2013-05-29 14:16:25'),(48,2,'marcink',48,'RC/rc2/test3','','started_following_repo','2013-05-29 14:16:25'),(49,2,'marcink',49,'csa-armstrong','','started_following_repo','2013-05-29 14:16:26'),(50,2,'marcink',50,'pyramidpypi','','started_following_repo','2013-05-29 14:16:26'),(51,2,'marcink',51,'RC/lol/haha','','started_following_repo','2013-05-29 14:16:26'),(52,2,'marcink',52,'csa-io','','started_following_repo','2013-05-29 14:16:26'),(53,2,'marcink',53,'enc-envelope','','started_following_repo','2013-05-29 14:16:26'),(54,2,'marcink',54,'RC/gogo2','','started_following_repo','2013-05-29 14:16:26'),(55,2,'marcink',55,'csa-libcloud','','started_following_repo','2013-05-29 14:16:27'),(56,2,'marcink',56,'RC/git-test','','started_following_repo','2013-05-29 14:16:27'),(57,2,'marcink',57,'RC/rc2/test','','started_following_repo','2013-05-29 14:16:27'),(58,2,'marcink',58,'salt','','started_following_repo','2013-05-29 14:16:27'),(59,2,'marcink',59,'RC/kiall-nova','','started_following_repo','2013-05-29 14:16:27');
/*!40000 ALTER TABLE `user_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_repo_group_to_perm`
--

DROP TABLE IF EXISTS `user_repo_group_to_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_repo_group_to_perm` (
  `group_to_perm_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`group_to_perm_id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`,`permission_id`),
  UNIQUE KEY `group_to_perm_id` (`group_to_perm_id`),
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `user_repo_group_to_perm_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `user_repo_group_to_perm_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`),
  CONSTRAINT `user_repo_group_to_perm_ibfk_3` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_repo_group_to_perm`
--

LOCK TABLES `user_repo_group_to_perm` WRITE;
/*!40000 ALTER TABLE `user_repo_group_to_perm` DISABLE KEYS */;
INSERT INTO `user_repo_group_to_perm` VALUES (1,1,1,6),(2,1,2,6),(3,1,3,6),(4,1,4,6),(5,1,5,6),(6,1,6,6),(7,1,7,6),(8,1,8,6);
/*!40000 ALTER TABLE `user_repo_group_to_perm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_to_notification`
--

DROP TABLE IF EXISTS `user_to_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_to_notification` (
  `user_id` int(11) NOT NULL,
  `notification_id` int(11) NOT NULL,
  `read` tinyint(1) DEFAULT NULL,
  `sent_on` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`,`notification_id`),
  UNIQUE KEY `user_id` (`user_id`,`notification_id`),
  KEY `notification_id` (`notification_id`),
  CONSTRAINT `user_to_notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `user_to_notification_ibfk_2` FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_to_notification`
--

LOCK TABLES `user_to_notification` WRITE;
/*!40000 ALTER TABLE `user_to_notification` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_to_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_to_perm`
--

DROP TABLE IF EXISTS `user_to_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_to_perm` (
  `user_to_perm_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`user_to_perm_id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  UNIQUE KEY `user_to_perm_id` (`user_to_perm_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `user_to_perm_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `user_to_perm_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_to_perm`
--

LOCK TABLES `user_to_perm` WRITE;
/*!40000 ALTER TABLE `user_to_perm` DISABLE KEYS */;
INSERT INTO `user_to_perm` VALUES (4,1,2),(5,1,6),(2,1,11),(3,1,13),(1,1,15);
/*!40000 ALTER TABLE `user_to_perm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `admin` tinyint(1) DEFAULT NULL,
  `firstname` varchar(255) DEFAULT NULL,
  `lastname` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `ldap_dn` varchar(255) DEFAULT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `inherit_default_permissions` tinyint(1) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `u_email_idx` (`email`),
  KEY `u_username_idx` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'default','$2a$10$k/day.yz9z8QtPF1Mj8ZzOJ794CJS3e4bJ2OCHftGCfCCdRfGKRPm',1,0,'Anonymous','User','anonymous@rhodecode.org',NULL,NULL,'4fc339e026489778a8b80deb0ef2cce571bf02d0',1),(2,'marcink','$2a$10$piApcGV3vLj1hC6oEH6MROyDMwt5MAnu6vaN8Rwq.069FJCdgfNUC',1,1,'RhodeCode','Admin','marcin@appzonaut.com',NULL,NULL,'e69148c8899d2ae291fe0bd79be7f085bf4cb2a6',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_group_repo_group_to_perm`
--

DROP TABLE IF EXISTS `users_group_repo_group_to_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_group_repo_group_to_perm` (
  `users_group_repo_group_to_perm_id` int(11) NOT NULL AUTO_INCREMENT,
  `users_group_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`users_group_repo_group_to_perm_id`),
  UNIQUE KEY `users_group_id` (`users_group_id`,`group_id`),
  UNIQUE KEY `users_group_repo_group_to_perm_id` (`users_group_repo_group_to_perm_id`),
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `users_group_repo_group_to_perm_ibfk_1` FOREIGN KEY (`users_group_id`) REFERENCES `users_groups` (`users_group_id`),
  CONSTRAINT `users_group_repo_group_to_perm_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`),
  CONSTRAINT `users_group_repo_group_to_perm_ibfk_3` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_group_repo_group_to_perm`
--

LOCK TABLES `users_group_repo_group_to_perm` WRITE;
/*!40000 ALTER TABLE `users_group_repo_group_to_perm` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_group_repo_group_to_perm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_group_repo_to_perm`
--

DROP TABLE IF EXISTS `users_group_repo_to_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_group_repo_to_perm` (
  `users_group_to_perm_id` int(11) NOT NULL AUTO_INCREMENT,
  `users_group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `repository_id` int(11) NOT NULL,
  PRIMARY KEY (`users_group_to_perm_id`),
  UNIQUE KEY `repository_id` (`repository_id`,`users_group_id`,`permission_id`),
  UNIQUE KEY `users_group_to_perm_id` (`users_group_to_perm_id`),
  KEY `users_group_id` (`users_group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `users_group_repo_to_perm_ibfk_1` FOREIGN KEY (`users_group_id`) REFERENCES `users_groups` (`users_group_id`),
  CONSTRAINT `users_group_repo_to_perm_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`),
  CONSTRAINT `users_group_repo_to_perm_ibfk_3` FOREIGN KEY (`repository_id`) REFERENCES `repositories` (`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_group_repo_to_perm`
--

LOCK TABLES `users_group_repo_to_perm` WRITE;
/*!40000 ALTER TABLE `users_group_repo_to_perm` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_group_repo_to_perm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_group_to_perm`
--

DROP TABLE IF EXISTS `users_group_to_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_group_to_perm` (
  `users_group_to_perm_id` int(11) NOT NULL AUTO_INCREMENT,
  `users_group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`users_group_to_perm_id`),
  UNIQUE KEY `users_group_id` (`users_group_id`,`permission_id`),
  UNIQUE KEY `users_group_to_perm_id` (`users_group_to_perm_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `users_group_to_perm_ibfk_1` FOREIGN KEY (`users_group_id`) REFERENCES `users_groups` (`users_group_id`),
  CONSTRAINT `users_group_to_perm_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_group_to_perm`
--

LOCK TABLES `users_group_to_perm` WRITE;
/*!40000 ALTER TABLE `users_group_to_perm` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_group_to_perm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_groups` (
  `users_group_id` int(11) NOT NULL AUTO_INCREMENT,
  `users_group_name` varchar(255) NOT NULL,
  `users_group_active` tinyint(1) DEFAULT NULL,
  `users_group_inherit_default_permissions` tinyint(1) NOT NULL,
  PRIMARY KEY (`users_group_id`),
  UNIQUE KEY `users_group_id` (`users_group_id`),
  UNIQUE KEY `users_group_name` (`users_group_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups_members`
--

DROP TABLE IF EXISTS `users_groups_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_groups_members` (
  `users_group_member_id` int(11) NOT NULL AUTO_INCREMENT,
  `users_group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`users_group_member_id`),
  UNIQUE KEY `users_group_member_id` (`users_group_member_id`),
  KEY `users_group_id` (`users_group_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `users_groups_members_ibfk_1` FOREIGN KEY (`users_group_id`) REFERENCES `users_groups` (`users_group_id`),
  CONSTRAINT `users_groups_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups_members`
--

LOCK TABLES `users_groups_members` WRITE;
/*!40000 ALTER TABLE `users_groups_members` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups_members` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-05-29 14:16:34
