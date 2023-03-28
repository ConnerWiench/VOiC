-- MySQL dump 10.13  Distrib 8.0.32, for Linux (x86_64)
--
-- Host: localhost    Database: voic_db
-- ------------------------------------------------------
-- Server version	8.0.32-0ubuntu0.22.10.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `court_case`
--

DROP TABLE IF EXISTS `court_case`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `court_case` (
  `case_number` int NOT NULL,
  `case_charge` varchar(45) NOT NULL,
  `case_verdict` varchar(45) NOT NULL,
  `case_facts` blob,
  `case_time_created` datetime NOT NULL,
  `case_preceed_number` int DEFAULT NULL,
  `case_released` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`case_number`),
  UNIQUE KEY `case_number_UNIQUE` (`case_number`),
  KEY `fk_case_succeed_number_idx` (`case_preceed_number`),
  CONSTRAINT `fk_case_preceed_number` FOREIGN KEY (`case_preceed_number`) REFERENCES `court_case` (`case_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `court_case`
--

LOCK TABLES `court_case` WRITE;
/*!40000 ALTER TABLE `court_case` DISABLE KEYS */;
/*!40000 ALTER TABLE `court_case` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `court_docs`
--

DROP TABLE IF EXISTS `court_docs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `court_docs` (
  `docs_title` varchar(45) NOT NULL,
  `docs_path` varchar(200) NOT NULL,
  `docs_type` varchar(45) NOT NULL,
  `docs_approved` tinyint NOT NULL DEFAULT '0',
  `docs_case` int DEFAULT NULL,
  PRIMARY KEY (`docs_title`),
  UNIQUE KEY `docs_path_UNIQUE` (`docs_path`),
  UNIQUE KEY `docs_title_UNIQUE` (`docs_title`),
  KEY `fk_docs_case_idx` (`docs_case`),
  CONSTRAINT `fk_docs_case` FOREIGN KEY (`docs_case`) REFERENCES `court_case` (`case_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `court_docs`
--

LOCK TABLES `court_docs` WRITE;
/*!40000 ALTER TABLE `court_docs` DISABLE KEYS */;
/*!40000 ALTER TABLE `court_docs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `court_user`
--

DROP TABLE IF EXISTS `court_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `court_user` (
  `user_name` varchar(45) NOT NULL,
  `user_first` varchar(45) NOT NULL,
  `user_last` varchar(45) NOT NULL,
  `user_level` varchar(45) NOT NULL,
  `user_created` datetime NOT NULL,
  `user_password` varchar(200) NOT NULL,
  `user_phone` varchar(45) NOT NULL,
  `user_question` varchar(45) NOT NULL,
  `user_answer` varchar(45) NOT NULL,
  PRIMARY KEY (`user_name`),
  UNIQUE KEY `user_name_UNIQUE` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `court_user`
--

LOCK TABLES `court_user` WRITE;
/*!40000 ALTER TABLE `court_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `court_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `junction_case_user`
--

DROP TABLE IF EXISTS `junction_case_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `junction_case_user` (
  `junction_user` varchar(45) NOT NULL,
  `junction_case` int NOT NULL,
  `junction_role` varchar(45) NOT NULL,
  PRIMARY KEY (`junction_user`,`junction_case`),
  KEY `fk_junction_case_idx` (`junction_case`),
  CONSTRAINT `fk_junction_case` FOREIGN KEY (`junction_case`) REFERENCES `court_case` (`case_number`),
  CONSTRAINT `fk_junction_user` FOREIGN KEY (`junction_user`) REFERENCES `court_user` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `junction_case_user`
--

LOCK TABLES `junction_case_user` WRITE;
/*!40000 ALTER TABLE `junction_case_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `junction_case_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-28 12:38:03
