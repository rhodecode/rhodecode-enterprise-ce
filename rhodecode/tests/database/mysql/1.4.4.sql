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
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cache_invalidation`
--

LOCK TABLES `cache_invalidation` WRITE;
/*!40000 ALTER TABLE `cache_invalidation` DISABLE KEYS */;
INSERT INTO `cache_invalidation` VALUES (1,'1RC/fakeclone','RC/fakeclone',0),(2,'1RC/muay','RC/muay',0),(3,'1RC/rc2/test2','RC/rc2/test2',0),(4,'1RC/rc2/test3','RC/rc2/test3',0),(5,'1RC/rc2/test4','RC/rc2/test4',0),(6,'1rhodecode-cli-gist','rhodecode-cli-gist',1),(7,'1RC/new','RC/new',0),(8,'1.rc_gist_store/32','.rc_gist_store/32',0),(9,'1vcs','vcs',1),(10,'1.rc_gist_store/36','.rc_gist_store/36',0),(11,'1.rc_gist_store/37','.rc_gist_store/37',0),(12,'1.rc_gist_store/39','.rc_gist_store/39',0),(13,'1remote-salt','remote-salt',1),(14,'1RC/INRC/trololo','RC/INRC/trololo',0),(15,'1quest','quest',1),(16,'1csa-hyperion','csa-hyperion',1),(17,'1rhodecode','rhodecode',1),(18,'1RC/origin-fork-fork','RC/origin-fork-fork',0),(19,'1.rc_gist_store/45','.rc_gist_store/45',0),(20,'1.rc_gist_store/44','.rc_gist_store/44',0),(21,'1.rc_gist_store/46','.rc_gist_store/46',0),(22,'1.rc_gist_store/41','.rc_gist_store/41',0),(23,'1.rc_gist_store/40','.rc_gist_store/40',0),(24,'1RC/gogo2','RC/gogo2',0),(25,'1.rc_gist_store/42','.rc_gist_store/42',0),(26,'1.rc_gist_store/49','.rc_gist_store/49',0),(27,'1.rc_gist_store/48','.rc_gist_store/48',0),(28,'1csa-collins','csa-collins',1),(29,'1.rc_gist_store/54','.rc_gist_store/54',0),(30,'1.rc_gist_store/55','.rc_gist_store/55',0),(31,'1.rc_gist_store/52','.rc_gist_store/52',0),(32,'1.rc_gist_store/53','.rc_gist_store/53',0),(33,'1.rc_gist_store/50','.rc_gist_store/50',0),(34,'1.rc_gist_store/51','.rc_gist_store/51',0),(35,'1BIG/android','BIG/android',0),(36,'1RC/gogo-fork','RC/gogo-fork',0),(37,'1RC/mygr/lol','RC/mygr/lol',0),(38,'1RC/hg-repo','RC/hg-repo',0),(39,'1RC/bin-ops','RC/bin-ops',0),(40,'1.rc_gist_store/xFvj6dFqqVK5vfsGP8PU','.rc_gist_store/xFvj6dFqqVK5vfsGP8PU',0),(41,'1rhodecode-git','rhodecode-git',1),(42,'1csa-io','csa-io',1),(43,'1RC/qweqwe-fork','RC/qweqwe-fork',0),(44,'1csa-libcloud','csa-libcloud',1),(45,'1waitress','waitress',1),(46,'1.rc_gist_store/8','.rc_gist_store/8',0),(47,'1.rc_gist_store/9','.rc_gist_store/9',0),(48,'1RC/foobar','RC/foobar',0),(49,'1.rc_gist_store/1','.rc_gist_store/1',0),(50,'1.rc_gist_store/3','.rc_gist_store/3',0),(51,'1.rc_gist_store/4','.rc_gist_store/4',0),(52,'1.rc_gist_store/5','.rc_gist_store/5',0),(53,'1.rc_gist_store/6','.rc_gist_store/6',0),(54,'1.rc_gist_store/7','.rc_gist_store/7',0),(55,'1csa-harmony','csa-harmony',1),(56,'1rhodecode-extensions','rhodecode-extensions',1),(57,'1csa-prometheus','csa-prometheus',1),(58,'1RC/empty-git','RC/empty-git',0),(59,'1csa-salt-states','csa-salt-states',1),(60,'1RC/Å‚Ä™cina','RC/Å‚Ä™cina',0),(61,'1rhodecode-premium','rhodecode-premium',1),(62,'1RC/qweqwe-fork2','RC/qweqwe-fork2',0),(63,'1RC/INRC/L2_NEW/lalalal','RC/INRC/L2_NEW/lalalal',0),(64,'1RC/INRC/L2_NEW/L3/repo_test_move','RC/INRC/L2_NEW/L3/repo_test_move',0),(65,'1RC/jap','RC/jap',0),(66,'1RC/origin','RC/origin',0),(67,'1rhodecode-cli-api','rhodecode-cli-api',1),(68,'1csa-armstrong','csa-armstrong',1),(69,'1.rc_gist_store/NAsB8cacjxnqdyZ8QUl3','.rc_gist_store/NAsB8cacjxnqdyZ8QUl3',0),(70,'1RC/lol/haha','RC/lol/haha',0),(71,'1enc-envelope','enc-envelope',1),(72,'1.rc_gist_store/43','.rc_gist_store/43',0),(73,'1RC/test','RC/test',0),(74,'1BIG/git','BIG/git',0),(75,'1RC/origin-fork','RC/origin-fork',0),(76,'1RC/trololo','RC/trololo',0),(77,'1.rc_gist_store/FLj8GunafFAVBnuTWDxU','.rc_gist_store/FLj8GunafFAVBnuTWDxU',0),(78,'1csa-unity','csa-unity',1),(79,'1RC/vcs-git','RC/vcs-git',0),(80,'1.rc_gist_store/12','.rc_gist_store/12',0),(81,'1.rc_gist_store/13','.rc_gist_store/13',0),(82,'1.rc_gist_store/10','.rc_gist_store/10',0),(83,'1.rc_gist_store/11','.rc_gist_store/11',0),(84,'1RC/kiall-nova','RC/kiall-nova',0),(85,'1RC/rc2/test','RC/rc2/test',0),(86,'1DOCS','DOCS',1),(87,'1RC/fork-remote','RC/fork-remote',0),(88,'1RC/git-pull-test','RC/git-pull-test',0),(89,'1pyramidpypi','pyramidpypi',1),(90,'1.rc_gist_store/aQpbufbhSac6FyvVHhmS','.rc_gist_store/aQpbufbhSac6FyvVHhmS',0),(91,'1csa-aldrin','csa-aldrin',1),(92,'1RC/Ä…qweqwe','RC/Ä…qweqwe',0),(93,'1.rc_gist_store/QL2GhrlKymNmrUJJy5js','.rc_gist_store/QL2GhrlKymNmrUJJy5js',0),(94,'1RC/git-test','RC/git-test',0),(95,'1salt','salt',1);
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
  KEY `cs_version_idx` (`version`),
  KEY `cs_revision_idx` (`revision`),
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
INSERT INTO `db_migrate_version` VALUES ('rhodecode_db_migrations','versions',7);
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'RC',NULL,'RC group',0),(2,'RC/rc2',1,'RC/rc2 group',0),(3,'.rc_gist_store',NULL,'.rc_gist_store group',0),(4,'RC/INRC',1,'RC/INRC group',0),(5,'BIG',NULL,'BIG group',0),(6,'RC/mygr',1,'RC/mygr group',0),(7,'RC/INRC/L2_NEW',4,'RC/INRC/L2_NEW group',0),(8,'RC/INRC/L2_NEW/L3',7,'RC/INRC/L2_NEW/L3 group',0),(9,'RC/lol',1,'RC/lol group',0);
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
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repo_to_perm`
--

LOCK TABLES `repo_to_perm` WRITE;
/*!40000 ALTER TABLE `repo_to_perm` DISABLE KEYS */;
INSERT INTO `repo_to_perm` VALUES (1,1,2,1),(2,1,2,2),(3,1,2,3),(4,1,2,4),(5,1,2,5),(6,1,2,6),(7,1,2,7),(8,1,2,8),(9,1,2,9),(10,1,2,10),(11,1,2,11),(12,1,2,12),(13,1,2,13),(14,1,2,14),(15,1,2,15),(16,1,2,16),(17,1,2,17),(18,1,2,18),(19,1,2,19),(20,1,2,20),(21,1,2,21),(22,1,2,22),(23,1,2,23),(24,1,2,24),(25,1,2,25),(26,1,2,26),(27,1,2,27),(28,1,2,28),(29,1,2,29),(30,1,2,30),(31,1,2,31),(32,1,2,32),(33,1,2,33),(34,1,2,34),(35,1,2,35),(36,1,2,36),(37,1,2,37),(38,1,2,38),(39,1,2,39),(40,1,2,40),(41,1,2,41),(42,1,2,42),(43,1,2,43),(44,1,2,44),(45,1,2,45),(46,1,2,46),(47,1,2,47),(48,1,2,48),(49,1,2,49),(50,1,2,50),(51,1,2,51),(52,1,2,52),(53,1,2,53),(54,1,2,54),(55,1,2,55),(56,1,2,56),(57,1,2,57),(58,1,2,58),(59,1,2,59),(60,1,2,60),(61,1,2,61),(62,1,2,62),(63,1,2,63),(64,1,2,64),(65,1,2,65),(66,1,2,66),(67,1,2,67),(68,1,2,68),(69,1,2,69),(70,1,2,70),(71,1,2,71),(72,1,2,72),(73,1,2,73),(74,1,2,74),(75,1,2,75),(76,1,2,76),(77,1,2,77),(78,1,2,78),(79,1,2,79),(80,1,2,80),(81,1,2,81),(82,1,2,82),(83,1,2,83),(84,1,2,84),(85,1,2,85),(86,1,2,86),(87,1,2,87),(88,1,2,88),(89,1,2,89),(90,1,2,90),(91,1,2,91),(92,1,2,92),(93,1,2,93),(94,1,2,94),(95,1,2,95);
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
  `fork_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`repo_id`),
  UNIQUE KEY `repo_name` (`repo_name`),
  UNIQUE KEY `repo_id` (`repo_id`),
  UNIQUE KEY `repo_name_2` (`repo_name`),
  KEY `user_id` (`user_id`),
  KEY `fork_id` (`fork_id`),
  KEY `group_id` (`group_id`),
  KEY `r_repo_name_idx` (`repo_name`),
  CONSTRAINT `repositories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `repositories_ibfk_2` FOREIGN KEY (`fork_id`) REFERENCES `repositories` (`repo_id`),
  CONSTRAINT `repositories_ibfk_3` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repositories`
--

LOCK TABLES `repositories` WRITE;
/*!40000 ALTER TABLE `repositories` DISABLE KEYS */;
INSERT INTO `repositories` VALUES (1,'RC/fakeclone','http://user@vm/RC/fakeclone','git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:03','2013-05-29 14:10:03','tip',0,NULL,NULL,1),(2,'RC/muay',NULL,'hg',2,0,0,1,'RC/muay repository','2013-05-29 14:10:03','2013-05-29 14:10:03','tip',0,NULL,NULL,1),(3,'RC/rc2/test2',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,2),(4,'RC/rc2/test3',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,2),(5,'RC/rc2/test4',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,2),(6,'rhodecode-cli-gist',NULL,'hg',2,0,0,1,'rhodecode-cli-gist repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(7,'RC/new',NULL,'hg',2,0,0,1,'RC/new repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,1),(8,'.rc_gist_store/32',NULL,'hg',2,0,0,1,'.rc_gist_store/32 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(9,'vcs',NULL,'hg',2,0,0,1,'vcs repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(10,'.rc_gist_store/36',NULL,'hg',2,0,0,1,'.rc_gist_store/36 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(11,'.rc_gist_store/37',NULL,'hg',2,0,0,1,'.rc_gist_store/37 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(12,'.rc_gist_store/39',NULL,'hg',2,0,0,1,'.rc_gist_store/39 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(13,'remote-salt',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(14,'RC/INRC/trololo',NULL,'hg',2,0,0,1,'RC/INRC/trololo repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,4),(15,'quest',NULL,'hg',2,0,0,1,'quest repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(16,'csa-hyperion',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(17,'rhodecode',NULL,'hg',2,0,0,1,'rhodecode repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(18,'RC/origin-fork-fork',NULL,'hg',2,0,0,1,'RC/origin-fork-fork repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,1),(19,'.rc_gist_store/45',NULL,'hg',2,0,0,1,'.rc_gist_store/45 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(20,'.rc_gist_store/44',NULL,'hg',2,0,0,1,'.rc_gist_store/44 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(21,'.rc_gist_store/46',NULL,'hg',2,0,0,1,'.rc_gist_store/46 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(22,'.rc_gist_store/41',NULL,'hg',2,0,0,1,'.rc_gist_store/41 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(23,'.rc_gist_store/40',NULL,'hg',2,0,0,1,'.rc_gist_store/40 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(24,'RC/gogo2',NULL,'hg',2,0,0,1,'RC/gogo2 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,1),(25,'.rc_gist_store/42',NULL,'hg',2,0,0,1,'.rc_gist_store/42 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(26,'.rc_gist_store/49',NULL,'hg',2,0,0,1,'.rc_gist_store/49 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(27,'.rc_gist_store/48',NULL,'hg',2,0,0,1,'.rc_gist_store/48 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(28,'csa-collins',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,NULL),(29,'.rc_gist_store/54',NULL,'hg',2,0,0,1,'.rc_gist_store/54 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(30,'.rc_gist_store/55',NULL,'hg',2,0,0,1,'.rc_gist_store/55 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(31,'.rc_gist_store/52',NULL,'hg',2,0,0,1,'.rc_gist_store/52 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(32,'.rc_gist_store/53',NULL,'hg',2,0,0,1,'.rc_gist_store/53 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(33,'.rc_gist_store/50',NULL,'hg',2,0,0,1,'.rc_gist_store/50 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(34,'.rc_gist_store/51',NULL,'hg',2,0,0,1,'.rc_gist_store/51 repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,3),(35,'BIG/android',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,5),(36,'RC/gogo-fork',NULL,'hg',2,0,0,1,'RC/gogo-fork repository','2013-05-29 14:10:04','2013-05-29 14:10:04','tip',0,NULL,NULL,1),(37,'RC/mygr/lol',NULL,'hg',2,0,0,1,'RC/mygr/lol repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,6),(38,'RC/hg-repo',NULL,'hg',2,0,0,1,'RC/hg-repo repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(39,'RC/bin-ops',NULL,'hg',2,0,0,1,'RC/bin-ops repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(40,'.rc_gist_store/xFvj6dFqqVK5vfsGP8PU',NULL,'hg',2,0,0,1,'.rc_gist_store/xFvj6dFqqVK5vfsGP8PU repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(41,'rhodecode-git',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(42,'csa-io',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(43,'RC/qweqwe-fork',NULL,'hg',2,0,0,1,'RC/qweqwe-fork repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(44,'csa-libcloud',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(45,'waitress',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(46,'.rc_gist_store/8',NULL,'hg',2,0,0,1,'.rc_gist_store/8 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(47,'.rc_gist_store/9',NULL,'hg',2,0,0,1,'.rc_gist_store/9 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(48,'RC/foobar',NULL,'hg',2,0,0,1,'RC/foobar repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(49,'.rc_gist_store/1',NULL,'hg',2,0,0,1,'.rc_gist_store/1 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(50,'.rc_gist_store/3',NULL,'hg',2,0,0,1,'.rc_gist_store/3 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(51,'.rc_gist_store/4',NULL,'hg',2,0,0,1,'.rc_gist_store/4 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(52,'.rc_gist_store/5',NULL,'hg',2,0,0,1,'.rc_gist_store/5 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(53,'.rc_gist_store/6',NULL,'hg',2,0,0,1,'.rc_gist_store/6 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(54,'.rc_gist_store/7',NULL,'hg',2,0,0,1,'.rc_gist_store/7 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,3),(55,'csa-harmony',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(56,'rhodecode-extensions',NULL,'hg',2,0,0,1,'rhodecode-extensions repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(57,'csa-prometheus',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(58,'RC/empty-git',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(59,'csa-salt-states',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(60,'RC/Å‚Ä™cina',NULL,'hg',2,0,0,1,'RC/Å‚Ä™cina repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(61,'rhodecode-premium',NULL,'hg',2,0,0,1,'rhodecode-premium repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,NULL),(62,'RC/qweqwe-fork2',NULL,'hg',2,0,0,1,'RC/qweqwe-fork2 repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(63,'RC/INRC/L2_NEW/lalalal',NULL,'hg',2,0,0,1,'RC/INRC/L2_NEW/lalalal repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,7),(64,'RC/INRC/L2_NEW/L3/repo_test_move',NULL,'hg',2,0,0,1,'RC/INRC/L2_NEW/L3/repo_test_move repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,8),(65,'RC/jap',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(66,'RC/origin',NULL,'hg',2,0,0,1,'RC/origin repository','2013-05-29 14:10:05','2013-05-29 14:10:05','tip',0,NULL,NULL,1),(67,'rhodecode-cli-api',NULL,'hg',2,0,0,1,'rhodecode-cli-api repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(68,'csa-armstrong',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(69,'.rc_gist_store/NAsB8cacjxnqdyZ8QUl3',NULL,'hg',2,0,0,1,'.rc_gist_store/NAsB8cacjxnqdyZ8QUl3 repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(70,'RC/lol/haha',NULL,'hg',2,0,0,1,'RC/lol/haha repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,9),(71,'enc-envelope',NULL,'hg',2,0,0,1,'enc-envelope repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(72,'.rc_gist_store/43',NULL,'hg',2,0,0,1,'.rc_gist_store/43 repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(73,'RC/test',NULL,'hg',2,0,0,1,'RC/test repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(74,'BIG/git',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,5),(75,'RC/origin-fork',NULL,'hg',2,0,0,1,'RC/origin-fork repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(76,'RC/trololo',NULL,'hg',2,0,0,1,'RC/trololo repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(77,'.rc_gist_store/FLj8GunafFAVBnuTWDxU',NULL,'hg',2,0,0,1,'.rc_gist_store/FLj8GunafFAVBnuTWDxU repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(78,'csa-unity',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(79,'RC/vcs-git',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(80,'.rc_gist_store/12',NULL,'hg',2,0,0,1,'.rc_gist_store/12 repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(81,'.rc_gist_store/13',NULL,'hg',2,0,0,1,'.rc_gist_store/13 repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(82,'.rc_gist_store/10',NULL,'hg',2,0,0,1,'.rc_gist_store/10 repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(83,'.rc_gist_store/11',NULL,'hg',2,0,0,1,'.rc_gist_store/11 repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(84,'RC/kiall-nova',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(85,'RC/rc2/test',NULL,'hg',2,0,0,1,'RC/rc2/test repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,2),(86,'DOCS',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(87,'RC/fork-remote',NULL,'hg',2,0,0,1,'RC/fork-remote repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(88,'RC/git-pull-test',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(89,'pyramidpypi',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(90,'.rc_gist_store/aQpbufbhSac6FyvVHhmS',NULL,'hg',2,0,0,1,'.rc_gist_store/aQpbufbhSac6FyvVHhmS repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(91,'csa-aldrin',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL),(92,'RC/Ä…qweqwe',NULL,'hg',2,0,0,1,'RC/Ä…qweqwe repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(93,'.rc_gist_store/QL2GhrlKymNmrUJJy5js',NULL,'hg',2,0,0,1,'.rc_gist_store/QL2GhrlKymNmrUJJy5js repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,3),(94,'RC/git-test',NULL,'git',2,0,0,1,'Unnamed repository','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,1),(95,'salt',NULL,'git',2,0,0,1,'Unnamed repository; edit this file \'description\' to name the repository.\n','2013-05-29 14:10:06','2013-05-29 14:10:06','tip',0,NULL,NULL,NULL);
/*!40000 ALTER TABLE `repositories` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rhodecode_settings`
--

LOCK TABLES `rhodecode_settings` WRITE;
/*!40000 ALTER TABLE `rhodecode_settings` DISABLE KEYS */;
INSERT INTO `rhodecode_settings` VALUES (1,'realm','RhodeCode authentication'),(2,'title','RhodeCode'),(3,'ga_code',''),(4,'show_public_icon','True'),(5,'show_private_icon','True'),(6,'stylify_metatags','True'),(7,'ldap_active','false'),(8,'ldap_host',''),(9,'ldap_port','389'),(10,'ldap_tls_kind','PLAIN'),(11,'ldap_tls_reqcert',''),(12,'ldap_dn_user',''),(13,'ldap_dn_pass',''),(14,'ldap_base_dn',''),(15,'ldap_filter',''),(16,'ldap_search_scope',''),(17,'ldap_attr_login',''),(18,'ldap_attr_firstname',''),(19,'ldap_attr_lastname',''),(20,'ldap_attr_email','');
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
INSERT INTO `rhodecode_ui` VALUES (1,'hooks','changegroup.update','hg update >&2',1),(2,'hooks','changegroup.repo_size','python:rhodecode.lib.hooks.repo_size',1),(3,'hooks','changegroup.push_logger','python:rhodecode.lib.hooks.log_push_action',1),(4,'hooks','prechangegroup.pre_push','python:rhodecode.lib.hooks.pre_push',1),(5,'hooks','outgoing.pull_logger','python:rhodecode.lib.hooks.log_pull_action',1),(6,'hooks','preoutgoing.pre_pull','python:rhodecode.lib.hooks.pre_pull',1),(7,'extensions','largefiles','',1),(8,'extensions','hgsubversion','',0),(9,'extensions','hggit','',0),(10,'web','push_ssl','1',1),(11,'web','allow_archive','gz zip bz2',1),(12,'web','allow_push','*',1),(13,'web','baseurl','/',1),(14,'paths','/','/mnt/hgfs/workspace-python',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_followings`
--

LOCK TABLES `user_followings` WRITE;
/*!40000 ALTER TABLE `user_followings` DISABLE KEYS */;
INSERT INTO `user_followings` VALUES (1,2,1,NULL,'2013-05-29 14:10:03'),(2,2,2,NULL,'2013-05-29 14:10:03'),(3,2,3,NULL,'2013-05-29 14:10:04'),(4,2,4,NULL,'2013-05-29 14:10:04'),(5,2,5,NULL,'2013-05-29 14:10:04'),(6,2,6,NULL,'2013-05-29 14:10:04'),(7,2,7,NULL,'2013-05-29 14:10:04'),(8,2,8,NULL,'2013-05-29 14:10:04'),(9,2,9,NULL,'2013-05-29 14:10:04'),(10,2,10,NULL,'2013-05-29 14:10:04'),(11,2,11,NULL,'2013-05-29 14:10:04'),(12,2,12,NULL,'2013-05-29 14:10:04'),(13,2,13,NULL,'2013-05-29 14:10:04'),(14,2,14,NULL,'2013-05-29 14:10:04'),(15,2,15,NULL,'2013-05-29 14:10:04'),(16,2,16,NULL,'2013-05-29 14:10:04'),(17,2,17,NULL,'2013-05-29 14:10:04'),(18,2,18,NULL,'2013-05-29 14:10:04'),(19,2,19,NULL,'2013-05-29 14:10:04'),(20,2,20,NULL,'2013-05-29 14:10:04'),(21,2,21,NULL,'2013-05-29 14:10:04'),(22,2,22,NULL,'2013-05-29 14:10:04'),(23,2,23,NULL,'2013-05-29 14:10:04'),(24,2,24,NULL,'2013-05-29 14:10:04'),(25,2,25,NULL,'2013-05-29 14:10:04'),(26,2,26,NULL,'2013-05-29 14:10:04'),(27,2,27,NULL,'2013-05-29 14:10:04'),(28,2,28,NULL,'2013-05-29 14:10:04'),(29,2,29,NULL,'2013-05-29 14:10:04'),(30,2,30,NULL,'2013-05-29 14:10:04'),(31,2,31,NULL,'2013-05-29 14:10:04'),(32,2,32,NULL,'2013-05-29 14:10:04'),(33,2,33,NULL,'2013-05-29 14:10:04'),(34,2,34,NULL,'2013-05-29 14:10:04'),(35,2,35,NULL,'2013-05-29 14:10:04'),(36,2,36,NULL,'2013-05-29 14:10:05'),(37,2,37,NULL,'2013-05-29 14:10:05'),(38,2,38,NULL,'2013-05-29 14:10:05'),(39,2,39,NULL,'2013-05-29 14:10:05'),(40,2,40,NULL,'2013-05-29 14:10:05'),(41,2,41,NULL,'2013-05-29 14:10:05'),(42,2,42,NULL,'2013-05-29 14:10:05'),(43,2,43,NULL,'2013-05-29 14:10:05'),(44,2,44,NULL,'2013-05-29 14:10:05'),(45,2,45,NULL,'2013-05-29 14:10:05'),(46,2,46,NULL,'2013-05-29 14:10:05'),(47,2,47,NULL,'2013-05-29 14:10:05'),(48,2,48,NULL,'2013-05-29 14:10:05'),(49,2,49,NULL,'2013-05-29 14:10:05'),(50,2,50,NULL,'2013-05-29 14:10:05'),(51,2,51,NULL,'2013-05-29 14:10:05'),(52,2,52,NULL,'2013-05-29 14:10:05'),(53,2,53,NULL,'2013-05-29 14:10:05'),(54,2,54,NULL,'2013-05-29 14:10:05'),(55,2,55,NULL,'2013-05-29 14:10:05'),(56,2,56,NULL,'2013-05-29 14:10:05'),(57,2,57,NULL,'2013-05-29 14:10:05'),(58,2,58,NULL,'2013-05-29 14:10:05'),(59,2,59,NULL,'2013-05-29 14:10:05'),(60,2,60,NULL,'2013-05-29 14:10:05'),(61,2,61,NULL,'2013-05-29 14:10:05'),(62,2,62,NULL,'2013-05-29 14:10:05'),(63,2,63,NULL,'2013-05-29 14:10:05'),(64,2,64,NULL,'2013-05-29 14:10:05'),(65,2,65,NULL,'2013-05-29 14:10:05'),(66,2,66,NULL,'2013-05-29 14:10:06'),(67,2,67,NULL,'2013-05-29 14:10:06'),(68,2,68,NULL,'2013-05-29 14:10:06'),(69,2,69,NULL,'2013-05-29 14:10:06'),(70,2,70,NULL,'2013-05-29 14:10:06'),(71,2,71,NULL,'2013-05-29 14:10:06'),(72,2,72,NULL,'2013-05-29 14:10:06'),(73,2,73,NULL,'2013-05-29 14:10:06'),(74,2,74,NULL,'2013-05-29 14:10:06'),(75,2,75,NULL,'2013-05-29 14:10:06'),(76,2,76,NULL,'2013-05-29 14:10:06'),(77,2,77,NULL,'2013-05-29 14:10:06'),(78,2,78,NULL,'2013-05-29 14:10:06'),(79,2,79,NULL,'2013-05-29 14:10:06'),(80,2,80,NULL,'2013-05-29 14:10:06'),(81,2,81,NULL,'2013-05-29 14:10:06'),(82,2,82,NULL,'2013-05-29 14:10:06'),(83,2,83,NULL,'2013-05-29 14:10:06'),(84,2,84,NULL,'2013-05-29 14:10:06'),(85,2,85,NULL,'2013-05-29 14:10:06'),(86,2,86,NULL,'2013-05-29 14:10:06'),(87,2,87,NULL,'2013-05-29 14:10:06'),(88,2,88,NULL,'2013-05-29 14:10:06'),(89,2,89,NULL,'2013-05-29 14:10:06'),(90,2,90,NULL,'2013-05-29 14:10:06'),(91,2,91,NULL,'2013-05-29 14:10:06'),(92,2,92,NULL,'2013-05-29 14:10:06'),(93,2,93,NULL,'2013-05-29 14:10:06'),(94,2,94,NULL,'2013-05-29 14:10:06'),(95,2,95,NULL,'2013-05-29 14:10:06');
/*!40000 ALTER TABLE `user_followings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_logs`
--

DROP TABLE IF EXISTS `user_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_logs` (
  `user_log_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_logs`
--

LOCK TABLES `user_logs` WRITE;
/*!40000 ALTER TABLE `user_logs` DISABLE KEYS */;
INSERT INTO `user_logs` VALUES (1,2,1,'RC/fakeclone','','started_following_repo','2013-05-29 14:10:03'),(2,2,2,'RC/muay','','started_following_repo','2013-05-29 14:10:03'),(3,2,3,'RC/rc2/test2','','started_following_repo','2013-05-29 14:10:04'),(4,2,4,'RC/rc2/test3','','started_following_repo','2013-05-29 14:10:04'),(5,2,5,'RC/rc2/test4','','started_following_repo','2013-05-29 14:10:04'),(6,2,6,'rhodecode-cli-gist','','started_following_repo','2013-05-29 14:10:04'),(7,2,7,'RC/new','','started_following_repo','2013-05-29 14:10:04'),(8,2,8,'.rc_gist_store/32','','started_following_repo','2013-05-29 14:10:04'),(9,2,9,'vcs','','started_following_repo','2013-05-29 14:10:04'),(10,2,10,'.rc_gist_store/36','','started_following_repo','2013-05-29 14:10:04'),(11,2,11,'.rc_gist_store/37','','started_following_repo','2013-05-29 14:10:04'),(12,2,12,'.rc_gist_store/39','','started_following_repo','2013-05-29 14:10:04'),(13,2,13,'remote-salt','','started_following_repo','2013-05-29 14:10:04'),(14,2,14,'RC/INRC/trololo','','started_following_repo','2013-05-29 14:10:04'),(15,2,15,'quest','','started_following_repo','2013-05-29 14:10:04'),(16,2,16,'csa-hyperion','','started_following_repo','2013-05-29 14:10:04'),(17,2,17,'rhodecode','','started_following_repo','2013-05-29 14:10:04'),(18,2,18,'RC/origin-fork-fork','','started_following_repo','2013-05-29 14:10:04'),(19,2,19,'.rc_gist_store/45','','started_following_repo','2013-05-29 14:10:04'),(20,2,20,'.rc_gist_store/44','','started_following_repo','2013-05-29 14:10:04'),(21,2,21,'.rc_gist_store/46','','started_following_repo','2013-05-29 14:10:04'),(22,2,22,'.rc_gist_store/41','','started_following_repo','2013-05-29 14:10:04'),(23,2,23,'.rc_gist_store/40','','started_following_repo','2013-05-29 14:10:04'),(24,2,24,'RC/gogo2','','started_following_repo','2013-05-29 14:10:04'),(25,2,25,'.rc_gist_store/42','','started_following_repo','2013-05-29 14:10:04'),(26,2,26,'.rc_gist_store/49','','started_following_repo','2013-05-29 14:10:04'),(27,2,27,'.rc_gist_store/48','','started_following_repo','2013-05-29 14:10:04'),(28,2,28,'csa-collins','','started_following_repo','2013-05-29 14:10:04'),(29,2,29,'.rc_gist_store/54','','started_following_repo','2013-05-29 14:10:04'),(30,2,30,'.rc_gist_store/55','','started_following_repo','2013-05-29 14:10:04'),(31,2,31,'.rc_gist_store/52','','started_following_repo','2013-05-29 14:10:04'),(32,2,32,'.rc_gist_store/53','','started_following_repo','2013-05-29 14:10:04'),(33,2,33,'.rc_gist_store/50','','started_following_repo','2013-05-29 14:10:04'),(34,2,34,'.rc_gist_store/51','','started_following_repo','2013-05-29 14:10:04'),(35,2,35,'BIG/android','','started_following_repo','2013-05-29 14:10:04'),(36,2,36,'RC/gogo-fork','','started_following_repo','2013-05-29 14:10:05'),(37,2,37,'RC/mygr/lol','','started_following_repo','2013-05-29 14:10:05'),(38,2,38,'RC/hg-repo','','started_following_repo','2013-05-29 14:10:05'),(39,2,39,'RC/bin-ops','','started_following_repo','2013-05-29 14:10:05'),(40,2,40,'.rc_gist_store/xFvj6dFqqVK5vfsGP8PU','','started_following_repo','2013-05-29 14:10:05'),(41,2,41,'rhodecode-git','','started_following_repo','2013-05-29 14:10:05'),(42,2,42,'csa-io','','started_following_repo','2013-05-29 14:10:05'),(43,2,43,'RC/qweqwe-fork','','started_following_repo','2013-05-29 14:10:05'),(44,2,44,'csa-libcloud','','started_following_repo','2013-05-29 14:10:05'),(45,2,45,'waitress','','started_following_repo','2013-05-29 14:10:05'),(46,2,46,'.rc_gist_store/8','','started_following_repo','2013-05-29 14:10:05'),(47,2,47,'.rc_gist_store/9','','started_following_repo','2013-05-29 14:10:05'),(48,2,48,'RC/foobar','','started_following_repo','2013-05-29 14:10:05'),(49,2,49,'.rc_gist_store/1','','started_following_repo','2013-05-29 14:10:05'),(50,2,50,'.rc_gist_store/3','','started_following_repo','2013-05-29 14:10:05'),(51,2,51,'.rc_gist_store/4','','started_following_repo','2013-05-29 14:10:05'),(52,2,52,'.rc_gist_store/5','','started_following_repo','2013-05-29 14:10:05'),(53,2,53,'.rc_gist_store/6','','started_following_repo','2013-05-29 14:10:05'),(54,2,54,'.rc_gist_store/7','','started_following_repo','2013-05-29 14:10:05'),(55,2,55,'csa-harmony','','started_following_repo','2013-05-29 14:10:05'),(56,2,56,'rhodecode-extensions','','started_following_repo','2013-05-29 14:10:05'),(57,2,57,'csa-prometheus','','started_following_repo','2013-05-29 14:10:05'),(58,2,58,'RC/empty-git','','started_following_repo','2013-05-29 14:10:05'),(59,2,59,'csa-salt-states','','started_following_repo','2013-05-29 14:10:05'),(60,2,60,'RC/Å‚Ä™cina','','started_following_repo','2013-05-29 14:10:05'),(61,2,61,'rhodecode-premium','','started_following_repo','2013-05-29 14:10:05'),(62,2,62,'RC/qweqwe-fork2','','started_following_repo','2013-05-29 14:10:05'),(63,2,63,'RC/INRC/L2_NEW/lalalal','','started_following_repo','2013-05-29 14:10:05'),(64,2,64,'RC/INRC/L2_NEW/L3/repo_test_move','','started_following_repo','2013-05-29 14:10:05'),(65,2,65,'RC/jap','','started_following_repo','2013-05-29 14:10:05'),(66,2,66,'RC/origin','','started_following_repo','2013-05-29 14:10:05'),(67,2,67,'rhodecode-cli-api','','started_following_repo','2013-05-29 14:10:06'),(68,2,68,'csa-armstrong','','started_following_repo','2013-05-29 14:10:06'),(69,2,69,'.rc_gist_store/NAsB8cacjxnqdyZ8QUl3','','started_following_repo','2013-05-29 14:10:06'),(70,2,70,'RC/lol/haha','','started_following_repo','2013-05-29 14:10:06'),(71,2,71,'enc-envelope','','started_following_repo','2013-05-29 14:10:06'),(72,2,72,'.rc_gist_store/43','','started_following_repo','2013-05-29 14:10:06'),(73,2,73,'RC/test','','started_following_repo','2013-05-29 14:10:06'),(74,2,74,'BIG/git','','started_following_repo','2013-05-29 14:10:06'),(75,2,75,'RC/origin-fork','','started_following_repo','2013-05-29 14:10:06'),(76,2,76,'RC/trololo','','started_following_repo','2013-05-29 14:10:06'),(77,2,77,'.rc_gist_store/FLj8GunafFAVBnuTWDxU','','started_following_repo','2013-05-29 14:10:06'),(78,2,78,'csa-unity','','started_following_repo','2013-05-29 14:10:06'),(79,2,79,'RC/vcs-git','','started_following_repo','2013-05-29 14:10:06'),(80,2,80,'.rc_gist_store/12','','started_following_repo','2013-05-29 14:10:06'),(81,2,81,'.rc_gist_store/13','','started_following_repo','2013-05-29 14:10:06'),(82,2,82,'.rc_gist_store/10','','started_following_repo','2013-05-29 14:10:06'),(83,2,83,'.rc_gist_store/11','','started_following_repo','2013-05-29 14:10:06'),(84,2,84,'RC/kiall-nova','','started_following_repo','2013-05-29 14:10:06'),(85,2,85,'RC/rc2/test','','started_following_repo','2013-05-29 14:10:06'),(86,2,86,'DOCS','','started_following_repo','2013-05-29 14:10:06'),(87,2,87,'RC/fork-remote','','started_following_repo','2013-05-29 14:10:06'),(88,2,88,'RC/git-pull-test','','started_following_repo','2013-05-29 14:10:06'),(89,2,89,'pyramidpypi','','started_following_repo','2013-05-29 14:10:06'),(90,2,90,'.rc_gist_store/aQpbufbhSac6FyvVHhmS','','started_following_repo','2013-05-29 14:10:06'),(91,2,91,'csa-aldrin','','started_following_repo','2013-05-29 14:10:06'),(92,2,92,'RC/Ä…qweqwe','','started_following_repo','2013-05-29 14:10:06'),(93,2,93,'.rc_gist_store/QL2GhrlKymNmrUJJy5js','','started_following_repo','2013-05-29 14:10:06'),(94,2,94,'RC/git-test','','started_following_repo','2013-05-29 14:10:06'),(95,2,95,'salt','','started_following_repo','2013-05-29 14:10:06'),(96,2,NULL,'','','admin_created_users_group:group2','2013-05-29 14:10:52'),(97,2,NULL,'','','admin_updated_users_group:group2','2013-05-29 14:10:57'),(98,2,NULL,'','','admin_created_user:qwe','2013-05-29 14:11:08');
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_repo_group_to_perm`
--

LOCK TABLES `user_repo_group_to_perm` WRITE;
/*!40000 ALTER TABLE `user_repo_group_to_perm` DISABLE KEYS */;
INSERT INTO `user_repo_group_to_perm` VALUES (1,1,1,6),(2,1,2,6),(3,1,3,6),(4,1,4,6),(5,1,5,6),(6,1,6,6),(7,1,7,6),(8,1,8,6),(9,1,9,6);
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_to_perm`
--

LOCK TABLES `user_to_perm` WRITE;
/*!40000 ALTER TABLE `user_to_perm` DISABLE KEYS */;
INSERT INTO `user_to_perm` VALUES (4,1,2),(2,1,11),(3,1,13),(1,1,15);
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
  KEY `u_username_idx` (`username`),
  KEY `u_email_idx` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'default','$2a$10$.kEwJNTCxwIh0ReQphLNi..a1EwNg/xhTzZCTlYanrJbe4hvCRVem',1,0,'Anonymous','User','anonymous@rhodecode.org',NULL,NULL,'14256045ac36c160e6b260d0ee75afaf035eee33',1),(2,'marcink','$2a$10$OsOsKSTCj7KdhqExE3NuV.cuduXJLH0ZOgglMq0nBP0Tjo6xD7KYS',1,1,'RhodeCode','Admin','marcin@appzonaut.com',NULL,NULL,'1bb94114e81e70a1a039260c9b4eb477c06c9b88',1),(3,'qwe','$2a$10$bN/GP86J2DMChvwI/0OmpeXJmD2B/Lchkju4PhXBCh6dCadoPv9tO',1,0,'qweqwe','qweqw','qweqwe@qwe.org',NULL,NULL,'6f5b83382ec01bd9ee728bd41db69c7dd90a63a2',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
INSERT INTO `users_groups` VALUES (1,'group2',1,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups_members`
--

LOCK TABLES `users_groups_members` WRITE;
/*!40000 ALTER TABLE `users_groups_members` DISABLE KEYS */;
INSERT INTO `users_groups_members` VALUES (1,1,1),(2,1,2);
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

-- Dump completed on 2013-05-29 14:13:26
