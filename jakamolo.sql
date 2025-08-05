-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 05, 2025 at 12:36 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `jakamolo`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add blog post', 7, 'add_blogpost'),
(26, 'Can change blog post', 7, 'change_blogpost'),
(27, 'Can delete blog post', 7, 'delete_blogpost'),
(28, 'Can view blog post', 7, 'view_blogpost'),
(29, 'Can add contact', 8, 'add_contact'),
(30, 'Can change contact', 8, 'change_contact'),
(31, 'Can delete contact', 8, 'delete_contact'),
(32, 'Can view contact', 8, 'view_contact'),
(33, 'Can add education level', 9, 'add_educationlevel'),
(34, 'Can change education level', 9, 'change_educationlevel'),
(35, 'Can delete education level', 9, 'delete_educationlevel'),
(36, 'Can view education level', 9, 'view_educationlevel'),
(37, 'Can add event category', 10, 'add_eventcategory'),
(38, 'Can change event category', 10, 'change_eventcategory'),
(39, 'Can delete event category', 10, 'delete_eventcategory'),
(40, 'Can view event category', 10, 'view_eventcategory'),
(41, 'Can add event location', 11, 'add_eventlocation'),
(42, 'Can change event location', 11, 'change_eventlocation'),
(43, 'Can delete event location', 11, 'delete_eventlocation'),
(44, 'Can view event location', 11, 'view_eventlocation'),
(45, 'Can add image gallery', 12, 'add_imagegallery'),
(46, 'Can change image gallery', 12, 'change_imagegallery'),
(47, 'Can delete image gallery', 12, 'delete_imagegallery'),
(48, 'Can view image gallery', 12, 'view_imagegallery'),
(49, 'Can add message', 13, 'add_message'),
(50, 'Can change message', 13, 'change_message'),
(51, 'Can delete message', 13, 'delete_message'),
(52, 'Can view message', 13, 'view_message'),
(53, 'Can add user', 14, 'add_myuser'),
(54, 'Can change user', 14, 'change_myuser'),
(55, 'Can delete user', 14, 'delete_myuser'),
(56, 'Can view user', 14, 'view_myuser'),
(57, 'Can add portfolio item', 15, 'add_portfolioitem'),
(58, 'Can change portfolio item', 15, 'change_portfolioitem'),
(59, 'Can delete portfolio item', 15, 'delete_portfolioitem'),
(60, 'Can view portfolio item', 15, 'view_portfolioitem'),
(61, 'Can add sibling', 16, 'add_sibling'),
(62, 'Can change sibling', 16, 'change_sibling'),
(63, 'Can delete sibling', 16, 'delete_sibling'),
(64, 'Can view sibling', 16, 'view_sibling'),
(65, 'Can add task', 17, 'add_task'),
(66, 'Can change task', 17, 'change_task'),
(67, 'Can delete task', 17, 'delete_task'),
(68, 'Can view task', 17, 'view_task'),
(69, 'Can add support', 18, 'add_support'),
(70, 'Can change support', 18, 'change_support'),
(71, 'Can delete support', 18, 'delete_support'),
(72, 'Can view support', 18, 'view_support'),
(73, 'Can add notification', 19, 'add_notification'),
(74, 'Can change notification', 19, 'change_notification'),
(75, 'Can delete notification', 19, 'delete_notification'),
(76, 'Can view notification', 19, 'view_notification'),
(77, 'Can add event', 20, 'add_event'),
(78, 'Can change event', 20, 'change_event'),
(79, 'Can delete event', 20, 'delete_event'),
(80, 'Can view event', 20, 'view_event'),
(81, 'Can add activity', 21, 'add_activity'),
(82, 'Can change activity', 21, 'change_activity'),
(83, 'Can delete activity', 21, 'delete_activity'),
(84, 'Can view activity', 21, 'view_activity'),
(85, 'Can add certification', 22, 'add_certification'),
(86, 'Can change certification', 22, 'change_certification'),
(87, 'Can delete certification', 22, 'delete_certification'),
(88, 'Can view certification', 22, 'view_certification'),
(89, 'Can add contact submission', 23, 'add_contactsubmission'),
(90, 'Can change contact submission', 23, 'change_contactsubmission'),
(91, 'Can delete contact submission', 23, 'delete_contactsubmission'),
(92, 'Can view contact submission', 23, 'view_contactsubmission'),
(93, 'Can add newsletter subscriber', 24, 'add_newslettersubscriber'),
(94, 'Can change newsletter subscriber', 24, 'change_newslettersubscriber'),
(95, 'Can delete newsletter subscriber', 24, 'delete_newslettersubscriber'),
(96, 'Can view newsletter subscriber', 24, 'view_newslettersubscriber'),
(97, 'Can add project', 25, 'add_project'),
(98, 'Can change project', 25, 'change_project'),
(99, 'Can delete project', 25, 'delete_project'),
(100, 'Can view project', 25, 'view_project'),
(101, 'Can add skill', 26, 'add_skill'),
(102, 'Can change skill', 26, 'change_skill'),
(103, 'Can delete skill', 26, 'delete_skill'),
(104, 'Can view skill', 26, 'view_skill'),
(105, 'Can add blog comment', 27, 'add_blogcomment'),
(106, 'Can change blog comment', 27, 'change_blogcomment'),
(107, 'Can delete blog comment', 27, 'delete_blogcomment'),
(108, 'Can view blog comment', 27, 'view_blogcomment'),
(109, 'Can add faq', 28, 'add_faq'),
(110, 'Can change faq', 28, 'change_faq'),
(111, 'Can delete faq', 28, 'delete_faq'),
(112, 'Can view faq', 28, 'view_faq'),
(113, 'Can add job', 29, 'add_job'),
(114, 'Can change job', 29, 'change_job'),
(115, 'Can delete job', 29, 'delete_job'),
(116, 'Can view job', 29, 'view_job'),
(117, 'Can add testimonial', 30, 'add_testimonial'),
(118, 'Can change testimonial', 30, 'change_testimonial'),
(119, 'Can delete testimonial', 30, 'delete_testimonial'),
(120, 'Can view testimonial', 30, 'view_testimonial'),
(121, 'Can add volunteer', 31, 'add_volunteer'),
(122, 'Can change volunteer', 31, 'change_volunteer'),
(123, 'Can delete volunteer', 31, 'delete_volunteer'),
(124, 'Can view volunteer', 31, 'view_volunteer'),
(125, 'Can add donation', 32, 'add_donation'),
(126, 'Can change donation', 32, 'change_donation'),
(127, 'Can delete donation', 32, 'delete_donation'),
(128, 'Can view donation', 32, 'view_donation'),
(129, 'Can add job application', 33, 'add_jobapplication'),
(130, 'Can change job application', 33, 'change_jobapplication'),
(131, 'Can delete job application', 33, 'delete_jobapplication'),
(132, 'Can view job application', 33, 'view_jobapplication'),
(133, 'Can add sibling image', 34, 'add_siblingimage'),
(134, 'Can change sibling image', 34, 'change_siblingimage'),
(135, 'Can delete sibling image', 34, 'delete_siblingimage'),
(136, 'Can view sibling image', 34, 'view_siblingimage'),
(137, 'Can add news', 35, 'add_news'),
(138, 'Can change news', 35, 'change_news'),
(139, 'Can delete news', 35, 'delete_news'),
(140, 'Can view news', 35, 'view_news'),
(141, 'Can add my new model', 36, 'add_mynewmodel'),
(142, 'Can change my new model', 36, 'change_mynewmodel'),
(143, 'Can delete my new model', 36, 'delete_mynewmodel'),
(144, 'Can view my new model', 36, 'view_mynewmodel'),
(145, 'Can add my external model', 37, 'add_myexternalmodel'),
(146, 'Can change my external model', 37, 'change_myexternalmodel'),
(147, 'Can delete my external model', 37, 'delete_myexternalmodel'),
(148, 'Can view my external model', 37, 'view_myexternalmodel'),
(149, 'Can add my new model2', 38, 'add_mynewmodel2'),
(150, 'Can change my new model2', 38, 'change_mynewmodel2'),
(151, 'Can delete my new model2', 38, 'delete_mynewmodel2'),
(152, 'Can view my new model2', 38, 'view_mynewmodel2');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$600000$tsPQxClAHFYGagEs0cZ2uW$tdiGUzEhL8jFPVzv3FvN311GVtmoFdhyyzAF9Jwi8yc=', '2025-07-05 11:14:08.807958', 1, 'StoryTeller', '', '', 'fellomarley@gmail.com', 1, 1, '2025-02-17 15:30:37.955084'),
(4, 'pbkdf2_sha256$600000$FxdyW4jX1bYfuA5kqPa5zW$eOtSL7kw9XQpIgEbTPYPE6Uod7zNVT5qaiR6w/s2rKw=', '2025-04-14 11:18:26.001818', 0, 'Amanda', '', '', 'amanda@gmail.com', 0, 1, '2025-03-02 20:36:44.364255'),
(5, 'pbkdf2_sha256$600000$oF1xrtm7x3dHxEWJD75mKW$rozWrm1QSu2kBJSgdDqcPIchKIE+JljsmPiBRnsxFCo=', '2025-04-12 16:43:16.000000', 0, 'Ynnot', '', '', 'ynnoty@gmail.com', 0, 1, '2025-04-12 16:40:52.000000'),
(6, 'pbkdf2_sha256$600000$JjmRrm4zSFyiFND6gHZLnZ$5lKNBe4pqrtf4tij2OADasA9FK7CNI2Wl6HoMu9Yens=', NULL, 0, 'omondi', '', '', 'omondi@gmail.com', 0, 1, '2025-04-14 10:29:48.619330'),
(7, 'pbkdf2_sha256$600000$CsSkGmeJX5vdKt7jp7UIhs$aiihcEH+PhjvH9wvNnbc4ht4vjwRzgmpec65dZ1EfTI=', '2025-04-14 10:37:50.797711', 0, 'Fred', '', '', 'fred@gmail.com', 0, 1, '2025-04-14 10:36:01.529283'),
(8, 'pbkdf2_sha256$600000$wJFIr7tPpKFUKbvZhrwGwy$nMQsSoejNRgNdNNUqpVj5yew/cUEksyKN3GAorpU0UU=', '2025-04-14 10:50:48.348881', 0, 'Salima7', '', '', 'salima@gmail.com', 0, 1, '2025-04-14 10:47:03.974487'),
(9, 'pbkdf2_sha256$600000$Pkb2zydsCrP8DCB1c4dziG$0LjaACbzhh3OJci5XFIkQ0IGUSRKhVqv3xiRk0svWZs=', '2025-04-14 10:56:35.201002', 0, 'Kamau5', '', '', 'kamau@gmail.com', 0, 1, '2025-04-14 10:55:24.686199');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-04-14 06:31:18.687685', '5', 'Ynnot', 2, '[{\"changed\": {\"fields\": [\"Email address\"]}}]', 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session'),
(21, 'StoryTeller', 'activity'),
(27, 'StoryTeller', 'blogcomment'),
(7, 'StoryTeller', 'blogpost'),
(22, 'StoryTeller', 'certification'),
(8, 'StoryTeller', 'contact'),
(23, 'StoryTeller', 'contactsubmission'),
(32, 'StoryTeller', 'donation'),
(9, 'StoryTeller', 'educationlevel'),
(20, 'StoryTeller', 'event'),
(10, 'StoryTeller', 'eventcategory'),
(11, 'StoryTeller', 'eventlocation'),
(28, 'StoryTeller', 'faq'),
(12, 'StoryTeller', 'imagegallery'),
(29, 'StoryTeller', 'job'),
(33, 'StoryTeller', 'jobapplication'),
(13, 'StoryTeller', 'message'),
(37, 'StoryTeller', 'myexternalmodel'),
(36, 'StoryTeller', 'mynewmodel'),
(38, 'StoryTeller', 'mynewmodel2'),
(14, 'StoryTeller', 'myuser'),
(35, 'StoryTeller', 'news'),
(24, 'StoryTeller', 'newslettersubscriber'),
(19, 'StoryTeller', 'notification'),
(15, 'StoryTeller', 'portfolioitem'),
(25, 'StoryTeller', 'project'),
(16, 'StoryTeller', 'sibling'),
(34, 'StoryTeller', 'siblingimage'),
(26, 'StoryTeller', 'skill'),
(18, 'StoryTeller', 'support'),
(17, 'StoryTeller', 'task'),
(30, 'StoryTeller', 'testimonial'),
(31, 'StoryTeller', 'volunteer');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-02-17 15:27:54.342083'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-02-17 15:27:54.980099'),
(3, 'auth', '0001_initial', '2025-02-17 15:28:05.231178'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-02-17 15:28:05.906689'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-02-17 15:28:06.032819'),
(6, 'auth', '0004_alter_user_username_opts', '2025-02-17 15:28:06.106930'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-02-17 15:28:06.599553'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-02-17 15:28:06.631536'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-02-17 15:28:06.666514'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-02-17 15:28:06.750467'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-02-17 15:28:06.849560'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-02-17 15:28:06.933512'),
(13, 'auth', '0011_update_proxy_permissions', '2025-02-17 15:28:06.961496'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-02-17 15:28:07.050445'),
(15, 'StoryTeller', '0001_initial', '2025-02-17 15:28:24.727828'),
(16, 'admin', '0001_initial', '2025-02-17 15:28:26.751900'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-02-17 15:28:26.783402'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-02-17 15:28:26.851884'),
(19, 'sessions', '0001_initial', '2025-02-17 15:28:27.564403'),
(20, 'StoryTeller', '0002_blogcomment_certification_contactsubmission_newslettersubscriber_project_skill', '2025-02-19 08:43:53.004292'),
(21, 'StoryTeller', '0003_auto_20250219_1247', '2025-02-19 09:47:44.103030'),
(22, 'StoryTeller', '0004_auto_20250219_2324', '2025-02-19 20:24:13.750844'),
(23, 'StoryTeller', '0005_auto_20250221_0957', '2025-02-21 06:57:34.648986'),
(24, 'StoryTeller', '0006_contact_image', '2025-02-21 11:08:55.162881'),
(25, 'StoryTeller', '0007_auto_20250221_1504', '2025-02-21 12:04:52.050360'),
(26, 'StoryTeller', '0008_donation_faq_job_testimonial_volunteer', '2025-03-03 08:55:24.036014'),
(27, 'StoryTeller', '0009_auto_20250303_1255', '2025-03-03 09:55:16.125575'),
(28, 'StoryTeller', '0010_job_due_at', '2025-03-03 20:22:58.570641'),
(29, 'StoryTeller', '0011_alter_blogpost_updated_at', '2025-03-04 05:57:41.129940'),
(30, 'StoryTeller', '0012_auto_20250304_1724', '2025-03-04 14:25:08.832690'),
(31, 'StoryTeller', '0013_alter_portfolioitem_technology', '2025-03-04 15:17:52.473186'),
(32, 'StoryTeller', '0014_auto_20250305_2241', '2025-03-05 19:41:23.642752'),
(33, 'StoryTeller', '0015_alter_project_options_project_attachments_and_more', '2025-03-21 18:55:27.808861'),
(34, 'StoryTeller', '0016_project_categoty_alter_project_status', '2025-03-21 18:55:32.031049'),
(35, 'StoryTeller', '0017_blogtag_blogcomment_blogpost_tags_eventrsvp_and_more', '2025-03-21 18:56:03.150305'),
(36, 'StoryTeller', '0018_remove_job_application_link_job_job_field_and_more', '2025-03-21 18:56:04.068827'),
(37, 'StoryTeller', '0019_alter_job_posted_at', '2025-03-21 18:56:04.279019'),
(38, 'StoryTeller', '0020_remove_jobapplication_applicant_and_more', '2025-03-21 18:56:08.109727'),
(39, 'StoryTeller', '0021_alter_jobapplication_cover_letter', '2025-03-21 18:56:10.689527'),
(40, 'StoryTeller', '0022_remove_blogpost_tags_remove_eventrsvp_event_and_more', '2025-03-21 18:56:27.613964'),
(41, 'StoryTeller', '0023_jobapplication', '2025-03-21 18:56:31.271187'),
(42, 'StoryTeller', '0024_jobapplication_applicant_name', '2025-03-21 18:56:32.550455'),
(43, 'StoryTeller', '0025_alter_jobapplication_cover_letter', '2025-03-21 18:56:34.892093'),
(44, 'StoryTeller', '0026_remove_jobapplication_applicant', '2025-03-21 18:56:36.087445'),
(45, 'StoryTeller', '0027_jobapplication_applicant', '2025-03-21 18:56:37.601630'),
(46, 'StoryTeller', '0028_oursiblings', '2025-03-21 18:56:38.788397'),
(47, 'StoryTeller', '0029_siblingimage_delete_oursiblings', '2025-03-21 18:56:41.171177'),
(48, 'StoryTeller', '0030_remove_sibling_age', '2025-03-21 18:56:41.853744'),
(49, 'StoryTeller', '0031_sibling_age', '2025-03-21 18:56:42.202180'),
(50, 'StoryTeller', '0032_alter_sibling_options_remove_sibling_date', '2025-03-21 18:56:42.638430'),
(51, 'StoryTeller', '0033_alter_sibling_age', '2025-03-21 18:56:43.784896'),
(52, 'StoryTeller', '0034_alter_sibling_age', '2025-03-21 18:56:47.283364'),
(53, 'StoryTeller', '0035_blogpost_video_event_video_job_video_project_video_and_more', '2025-03-21 18:56:48.907559'),
(54, 'StoryTeller', '0036_alter_event_options_remove_event_date_and_more', '2025-03-21 18:56:49.569271'),
(55, 'StoryTeller', '0037_newspaper', '2025-04-12 07:30:04.455675'),
(56, 'StoryTeller', '0038_delete_newspaper', '2025-04-12 07:30:05.310843'),
(57, 'StoryTeller', '0039_auto_20250412_1029', '2025-04-12 07:30:07.215559'),
(58, 'StoryTeller', '0040_mynewmodel', '2025-04-12 08:57:40.889870'),
(59, 'StoryTeller', '0041_auto_20250412_1159', '2025-04-12 09:03:04.082923'),
(60, 'StoryTeller', '0042_myexternalmodel', '2025-04-12 09:09:22.770213'),
(61, 'StoryTeller', '0043_mynewmodel2_delete_myexternalmodel', '2025-04-12 09:11:03.813750'),
(62, 'StoryTeller', '0044_remove_mynewmodel2_my_new_model_delete_news_and_more', '2025-04-12 09:12:01.031146'),
(63, 'StoryTeller', '0045_imagegallery_video', '2025-04-15 15:25:52.691524'),
(64, 'StoryTeller', '0002_alter_myuser_email_alter_myuser_profilepic', '2025-07-29 12:45:33.679931');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('0vf8glxb0px7ujy9kia5wt8dpgwv77i4', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tuU4w:K7NF5X6QaxOuvaUjb4TRLEyAii4F5RVx9Tbai8YxHng', '2025-04-01 10:21:46.090775'),
('186izwip6mbsxuzbx2i04pkyl0hlxl3s', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1u3VS1:ED1jVt1Xk5OmlmGF8GwEIrPHQum6iOcSZrBLNphbdSw', '2025-04-26 07:38:53.528874'),
('1d53bhbu1c6dtplf8rntjw0ptnzr6i3d', '.eJxVjEEOwiAQRe_C2pCBFgou3fcMZIYZpWpoUtqV8e7apAvd_vfef6mE21rS1mRJE6uzMur0uxHmh9Qd8B3rbdZ5rusykd4VfdCmx5nleTncv4OCrXzrTthGL8w2GIDowXkHYANKTxAdoSe5wkAxRMgRiQf2HYtkNtQbDOr9Adc1OCs:1uY0qO:LE3Z6NR4FlAsjZkvzmp_u64U82HeX-TTc1YpLgEykXQ', '2025-07-19 11:14:08.813975'),
('2f67ne8t8c99ku6hrl33c844ncvls06u', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tvBUv:hwPa07I7lp_ul2mvvfRxjeCUn-mOKibpRUpixHduPuQ', '2025-04-03 08:43:29.360033'),
('3k8yaoe9ahfafwogwr0jdeebexsjohr4', '.eJxVjDsOwyAQRO9CHSE-4pcyfc6AFnYJTiKQjF1ZuXtsyUVSzrw3s7EI61LjOmiOE7Irk-zy2yXIL2oHwCe0R-e5t2WeEj8UftLB7x3pfTvdv4MKo-5rhQI9aFVssEpZksIZnaBQDhL3DNb5hMkID4aKN0hGG5lTCU6gUJp9vuSYN_8:1ug6XR:4pajxMalgNYlzhUzuxqxroK5A2t-t1LdwdmlYnWEui4', '2025-08-10 18:56:01.852658'),
('aee332csv9rkqczm9iheszy1pr4cp5is', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tp1vw:tBm7-UmSspuAUsaiRH0zXbCW4cshqh2kxMazhyO8G1Q', '2025-03-17 09:17:56.631703'),
('c7pss34tuz196pzkktf7nb8vtewbk0ul', '.eJxVjEEOwiAQRe_C2pDC2MK4dN8zEIYZbNVAUtqV8e7apAvd_vfef6kQt3UKW5MlzKwuyhh1-h0ppoeUnfA9llvVqZZ1mUnvij5o02NleV4P9-9gim361rmPxnbAMEhCQGI7YCYXxTsgQAPZokcmy-BS14s9AyORp96QSyLq_QEIvDhv:1ui8l3:X6H7_CWJVmqFtSkg6pmasbTO_tYHGEHkeWVzWg5Iw5c', '2025-08-16 09:42:29.654517'),
('l1m9su51fcb4hpaauvf16hew4pfiq5i1', '.eJxVjDsOwyAQRO9CHSE-4pcyfc6AFnYJTiKQjF1ZuXtsyUVSzrw3s7EI61LjOmiOE7Irk-zy2yXIL2oHwCe0R-e5t2WeEj8UftLB7x3pfTvdv4MKo-5rhQI9aFVssEpZksIZnaBQDhL3DNb5hMkID4aKN0hGG5lTCU6gUJp9vuSYN_8:1uhvB2:ZORHN5zyplmd9x4-12u0-cYtTdp7So04wBfPsemjf4I', '2025-08-15 19:12:24.571655'),
('llp25o72vqufnrwcoe7iacanl26v8kq0', '.eJxVjEEOwiAQRe_C2pCBFgou3fcMZIYZpWpoUtqV8e7apAvd_vfef6mE21rS1mRJE6uzMur0uxHmh9Qd8B3rbdZ5rusykd4VfdCmx5nleTncv4OCrXzrTthGL8w2GIDowXkHYANKTxAdoSe5wkAxRMgRiQf2HYtkNtQbDOr9Adc1OCs:1uLH0Y:Z4_3vaY9N85Me8lWQ8o4s7h6Lel9cdSlc9tKBw54c-s', '2025-06-14 07:51:58.762853'),
('m78j49bx7yyo1k79iovmbdxg9fag8dc7', '.eJxVjEEOwiAQRe_C2pCBFgou3fcMZIYZpWpoUtqV8e7apAvd_vfef6mE21rS1mRJE6uzMur0uxHmh9Qd8B3rbdZ5rusykd4VfdCmx5nleTncv4OCrXzrTthGL8w2GIDowXkHYANKTxAdoSe5wkAxRMgRiQf2HYtkNtQbDOr9Adc1OCs:1uHYIO:0XlFtQ4oh8tJMxwDN2oB2dAZvJEjzt4vy7MKhjUeU30', '2025-06-04 01:31:00.064233'),
('mes3zbqcranjv27v2z3ekjgbwfu5byrv', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tkgWU:wFXr-jPeM5ptuPQv1sOkcR_4_XV9PKH-G_pp8TBGeJU', '2025-03-05 09:37:42.564933'),
('o6yufqzd26fx7hraxtesekmy1p6irj2x', '.eJxVjEEOwiAQRe_C2pCBFgou3fcMZIYZpWpoUtqV8e7apAvd_vfef6mE21rS1mRJE6uzMur0uxHmh9Qd8B3rbdZ5rusykd4VfdCmx5nleTncv4OCrXzrTthGL8w2GIDowXkHYANKTxAdoSe5wkAxRMgRiQf2HYtkNtQbDOr9Adc1OCs:1u4MVQ:9kxg2XBJqYRfD8Ff_xNuK63T9UmjDZkJq4N3L6llPKQ', '2025-04-28 16:17:56.793748'),
('q3dr2g4qvsu893ndl8hgaxelc3k5bnof', '.eJxVjEEOwiAQRe_C2pCBFgou3fcMZIYZpWpoUtqV8e7apAvd_vfef6mE21rS1mRJE6uzMur0uxHmh9Qd8B3rbdZ5rusykd4VfdCmx5nleTncv4OCrXzrTthGL8w2GIDowXkHYANKTxAdoSe5wkAxRMgRiQf2HYtkNtQbDOr9Adc1OCs:1uEsuK:eT5uj-QaEoT7HdUVnwZTSOrYEZZ6g8zx6mNRMVviloU', '2025-05-27 16:55:08.375082'),
('qjjq3hzhyyhgnbrle8ug6p0sojxn1jkm', '.eJxVjDsOwjAQBe_iGlne9TeU9JzBWv9wANlSnFSIu0OkFNC-mXkv5mlbq99GXvyc2JkBsNPvGCg-cttJulO7dR57W5c58F3hBx382lN-Xg7376DSqN8aDYEU2UUI5IREo0qygFZoKx2SwpIBRYmYyCaMGlSYoKAkoybQRrP3B-L1NvU:1ujEew:NzB5ZlcSzu5DaEOwxiDTIPF5cGGFxALWQFRKVrWUnKg', '2025-08-19 10:12:42.936464'),
('rg1tm0oazd6g7zz9rcgaria4p8bjiv1n', '.eJxVjEEOwiAQRe_C2hAqMBSX7nsGMsOAVA0kpV0Z765NutDtf-_9lwi4rSVsPS1hZnERgxKn35EwPlLdCd-x3pqMra7LTHJX5EG7nBqn5_Vw_w4K9vKtIVvOPltKygOOYCLSEK0ip_1ZZ5XRAeSolXEqeWYgC2wNMCNYGEm8PxrpOHU:1ugjyC:EQNlsPBDEwdiYP5zCsMMkBAvL4_Xee04xJlktZLB-M0', '2025-08-12 13:02:16.978680'),
('tkqpfk6crf7e856cf1qt0p0nck6wlf5m', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tvhK1:wp7WzR95L_5R2_pW0excGKW3kpFaJjoLbD6aXv9li3U', '2025-04-04 18:42:21.273363'),
('tx06ccix4cz2kmxrlsqgw9e5xipzyz01', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tqy2T:tghg9Do8rT7_DqEFYuQTPf4nujhbJMoDME5nc7gUwN0', '2025-03-22 17:32:41.137311'),
('zv349pwy1w0noxxczjro9ychfk0sdc27', '.eJxVjEEOwiAQRe_C2hCGFgGX7nsGMjNMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJU1YXBer0uxHyQ-oO8h3rbdY813WZSO-KPmjTw5zleT3cv4OCrXzr7uwFHZA1vePQA7ELhnzMzkbmESgIjS6C80ZCxxzQg0GLlG0UQ6DeH9nwN_E:1tr0Qr:Zis-mOgaVUIn5ZtiDV52exL8vVq7XrV5yCQCar7_6PY', '2025-03-22 20:06:01.845302');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_activity`
--

CREATE TABLE `storyteller_activity` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_activity`
--

INSERT INTO `storyteller_activity` (`id`, `title`, `description`, `created_at`, `user_id`) VALUES
(1, 'Attending Project Workshop', 'As a project manager, will be attending workshop for further studie', '2025-02-19 09:53:54.444293', 1),
(2, 'sdrtyh', 'zdfgjhmn', '2025-02-19 09:54:11.557828', 1);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_blogpost`
--

CREATE TABLE `storyteller_blogpost` (
  `id` bigint(20) NOT NULL,
  `title` varchar(100) NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `author_id` bigint(20) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_blogpost`
--

INSERT INTO `storyteller_blogpost` (`id`, `title`, `content`, `created_at`, `updated_at`, `image`, `author_id`, `status`, `video`) VALUES
(1, 'Waititu crisis', 'Waititu to pay 53.3million or serve 12yrs in prison', '2025-02-18 17:49:54.167512', '2025-02-18 17:49:54.167512', 'blog_images/Buore.JPG', NULL, NULL, NULL),
(2, 'AU election', 'Come 15th Feb, Raila is voted to be the AU chairman. Its also been announced if Raila doesnt win the election, it will be a calamicious crisis to doc Samoei', '2025-02-18 17:55:26.354138', '2025-02-18 17:55:26.354138', 'blog_images/judiciary_F5nziLd.webp', NULL, NULL, NULL),
(3, 'FelloMarley the programmer', 'My first website to bulid was about\' youth empowerment\"', '2025-02-18 17:59:51.140891', '2025-02-20 08:48:25.380439', 'blog_images/flag.jpeg', NULL, NULL, NULL),
(6, 'zxcdfgvb', 'xzxdfgbv', '2025-02-20 13:39:59.277793', '2025-02-20 13:39:59.277793', 'blog_images/carrots_tjrk5F4.jpg', NULL, NULL, NULL),
(8, 'dsfg', 'zxxcdffgg', '2025-03-04 06:39:44.359155', '2025-02-25 00:00:00.000000', 'blog_images/Rivals.jpg', 1, 'drafted', NULL),
(9, 'Sudan Tension', 'south Sudan leaders agrees to easen tension in the country. The country has been faced with severe internal attacks, leadership ideologies', '2025-03-04 09:44:04.223519', '2025-03-04 00:00:00.000000', 'blog_images/dandora.jpg', 2, 'published', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_certification`
--

CREATE TABLE `storyteller_certification` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `issuing_organization` varchar(255) NOT NULL,
  `date_issued` date NOT NULL,
  `credential_url` varchar(200) DEFAULT NULL,
  `certificate_pdf` varchar(100) DEFAULT NULL,
  `certificate_image` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_certification`
--

INSERT INTO `storyteller_certification` (`id`, `title`, `issuing_organization`, `date_issued`, `credential_url`, `certificate_pdf`, `certificate_image`) VALUES
(1, 'Cyberrity', 'link', '2025-01-31', 'https://www.linkedin.com/learning/the-cybersecurity-threat-landscape-18018064/examine-the-cybersecurity-threat-landscape?anchor=CERTIFICATE_LEARNING&autoplay=false', 'certificates/CertificateOfCompletion_The_Cybersecurity_Threat_Landscape.pdf', 'certificate_images/cybersecurity.png'),
(4, 'Django Certification', 'Linked In', '2025-04-05', 'https://www.linkedin.com/learning/certificates/e740ae141644dc59fb9a8aea2f8295f5928af84e8fb549f121a3d31b42400f6f', 'certificates/CertificateOfCompletion_Advanced_Python_Projects_Build_AI_Applications.pdf', 'certificate_images/django-certification.png');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_contact`
--

CREATE TABLE `storyteller_contact` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` int(11) NOT NULL,
  `date_created` datetime(6) DEFAULT NULL,
  `message` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_contact`
--

INSERT INTO `storyteller_contact` (`id`, `name`, `email`, `phone`, `date_created`, `message`) VALUES
(1, 'Salima Amanda', 'salima@gmail.com', 700786452, '2025-02-19 09:00:10.089873', 'Salima is happy with what you are doing'),
(2, 'Assiello Nomar', 'assielo@gmail.com', 78965434, '2025-02-19 12:41:29.223398', 'Impressive Felix');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_donation`
--

CREATE TABLE `storyteller_donation` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `message` longtext DEFAULT NULL,
  `anonymous` tinyint(1) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `date_donated` datetime(6) NOT NULL,
  `donor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_donation`
--

INSERT INTO `storyteller_donation` (`id`, `name`, `email`, `amount`, `message`, `anonymous`, `payment_method`, `transaction_id`, `date_donated`, `donor_id`) VALUES
(1, 'Assiello Nomar', 'assielo@gmail.com', 5.00, NULL, 0, 'mpesa', NULL, '2025-03-03 09:03:19.866629', NULL),
(2, 'music', 'jakamolo@outlook.com', 790.00, NULL, 0, 'bank_transfer', NULL, '2025-03-03 09:16:08.763875', NULL),
(3, 'Millicent Achieng', 'salima@gmail.com', 12.00, NULL, 0, 'paypal', NULL, '2025-03-03 20:29:32.494445', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_educationlevel`
--

CREATE TABLE `storyteller_educationlevel` (
  `id` bigint(20) NOT NULL,
  `level` varchar(100) NOT NULL,
  `school` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `Year` varchar(10) DEFAULT NULL,
  `Grade` varchar(20) DEFAULT NULL,
  `pdf_proof` varchar(100) DEFAULT NULL,
  `date` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_educationlevel`
--

INSERT INTO `storyteller_educationlevel` (`id`, `level`, `school`, `description`, `Year`, `Grade`, `pdf_proof`, `date`) VALUES
(1, 'Primary School', 'Ratta Primary School', 'This is where my journey began, laying the foundation for my academic and personal growth. I developed a keen interest in mathematics and science, which later influenced my career choice.', '2003-2012', 'C+', '', '2025-02-18 18:04:50.779406'),
(2, 'Secondary School', 'Ratta Secondary School', 'During these years, I strengthened my passion for technology and problem-solving. I actively participated in STEM competitions and computer science-', '2013- 2018', 'B-', '', '2025-02-18 18:10:18.030951'),
(3, 'Opus Dei', 'Kabarak University', 'At Kabarak University, I pursued a Bachelor\'s degree in Computer Science. I specialized in software development, artificial intelligence, and machine learning, gaining practical experience through projects and internships.', '2019- Date', 'Second class', '', '2025-02-18 18:11:22.184909');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_event`
--

CREATE TABLE `storyteller_event` (
  `id` bigint(20) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `guests` varchar(255) NOT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `host_id` bigint(20) DEFAULT NULL,
  `location_id` bigint(20) DEFAULT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `start_date` datetime(6) DEFAULT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_event`
--

INSERT INTO `storyteller_event` (`id`, `title`, `description`, `image`, `guests`, `category_id`, `host_id`, `location_id`, `end_date`, `start_date`, `video`) VALUES
(1, 'Tech Innovators Conference 2025', 'Join us for the annual Tech Innovators Conference, where industry leaders from around the world gather to discuss the latest trends in technology, innovation, and entrepreneurship. This year’s conference will feature keynote speakers from leading tech companies, panel discussions, and networking opportunities. Don’t miss out on this amazing event that brings together visionaries, entrepreneurs, and tech enthusiasts to explore the future of technology.', 'events_images/1730310059669.jpg', 'Vicky Amanda', 1, 1, 2, NULL, '2025-03-03 09:55:15.620868', NULL),
(3, 'Arts in the Musoleum Kisumu', 'Different arts are yet to be improvised in kisumu come 18th/08', 'events_images/im.jpg', 'lawrence Kosgei', 2, 1, 3, NULL, '2025-03-03 09:55:15.620868', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_eventcategory`
--

CREATE TABLE `storyteller_eventcategory` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_eventcategory`
--

INSERT INTO `storyteller_eventcategory` (`id`, `name`) VALUES
(1, 'Thika'),
(2, 'Arts');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_eventlocation`
--

CREATE TABLE `storyteller_eventlocation` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `address` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_eventlocation`
--

INSERT INTO `storyteller_eventlocation` (`id`, `name`, `address`) VALUES
(1, 'music', 'Music art'),
(2, 'Thika', '00100, Nairobi'),
(3, 'Kisumu', '71 Maseno');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_faq`
--

CREATE TABLE `storyteller_faq` (
  `id` bigint(20) NOT NULL,
  `question` varchar(255) NOT NULL,
  `answer` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_faq`
--

INSERT INTO `storyteller_faq` (`id`, `question`, `answer`, `created_at`) VALUES
(1, 'jhgftryjh', 'm,nbvgfjh', '2025-03-04 10:18:14.650651');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_imagegallery`
--

CREATE TABLE `storyteller_imagegallery` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `image` varchar(100) NOT NULL,
  `caption` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_imagegallery`
--

INSERT INTO `storyteller_imagegallery` (`id`, `title`, `image`, `caption`, `created_at`, `video`) VALUES
(1, 'South B', 'gallery_images/IMG_20240404_181640_1_dUiNaD7.jpg', 'Watching FKF gamese', '2025-02-18 18:18:25.647814', NULL),
(2, 'In Kinoo', 'gallery_images/IMG_20240203_190720_2_3TEzvuH.jpg', 'Metropolitan in Kinoo with my brother Tonny during my attatchment at Anniversary Towers, computer department', '2025-02-18 18:19:38.035690', NULL),
(3, 'Metropolitan in Kinoo with my brother Tonny during my attatchment at Anniversary Towers, computer department', 'gallery_images/IMG_202308225_223618276_UXMIaNB.jpg', 'on my way to Kapkures for job purpose', '2025-02-18 18:20:31.957441', ''),
(4, 'Innovation Day', 'gallery_images/IMG-20250724-WA0011.jpg', 'Innovation day at Kabarak', '2025-02-18 18:21:28.862004', ''),
(5, 'Kabarak University', 'gallery_images/IMG-20231206-WA0003_vNaOA0k.jpg', 'I mean business inside these walls', '2025-02-18 18:22:14.961469', ''),
(6, 'Oloika Lodge', 'gallery_images/Fel14.jpg', 'recreational day', '2025-02-18 18:23:12.973279', NULL),
(7, 'Visiting Ouko Mboya', 'gallery_images/IMG_20250330_142610_1.jpg', 'Paying a visit to our hero the late Tom for the achievements and freedom he gave to our luo community. Tom your name will not rest with us only,  but promise the generation will come to know how great you were to us.\r\n\r\nThanks Tom', '2025-02-18 18:26:37.469995', ''),
(8, 'KICC event', 'gallery_images/IMG-20240124-WA0049.jpg', 'Meeting with the strong delegates from Azimio chairedby Jadwong Raila and Martha Karua', '2025-02-18 18:27:42.478038', ''),
(9, 'Westgate', 'gallery_images/wst.jpg', 'When duty calls', '2025-02-19 09:50:43.540125', NULL),
(12, 'Football my passion', 'gallery_images/74c1e581e08c4cb6849db13eb598fbc9.jpg', 'Showcasing my talent', '2025-04-16 06:37:32.645371', ''),
(13, 'Football locating big men', 'gallery_images/IMG-20250330-WA0007.jpg', 'On our way to Nyayo stadium to spaketate our own Gor Mahia on a derby with AFC Leopords', '2025-04-16 06:41:43.007534', ''),
(15, 'Africa International University', 'gallery_images/IMG_20250704_094113_HDR.jpg', 'At graduation ceremony at Karen- Africa International University', '2025-07-05 11:15:59.219063', '');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_job`
--

CREATE TABLE `storyteller_job` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `job_type` varchar(50) NOT NULL,
  `description` longtext NOT NULL,
  `requirements` longtext DEFAULT NULL,
  `posted_at` datetime(6) NOT NULL,
  `due_at` date DEFAULT NULL,
  `application_link` varchar(200) DEFAULT NULL,
  `salary_range` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_job`
--

INSERT INTO `storyteller_job` (`id`, `title`, `company`, `location`, `job_type`, `description`, `requirements`, `posted_at`, `due_at`, `application_link`, `salary_range`) VALUES
(3, 'Youth Employment programs', 'open source', 'Kisumu, Nairobi and Kisii County', 'contract', 'this jobs have been set to create emplyment opportunities among the youths and reduce the crime rates due to frequent enemployment rates.', 'ID card', '2025-03-03 20:15:33.712353', '2025-04-06', 'https://github.com/Felixngwono/Personal-Web', '50000-78000'),
(5, 'Receptionist/Front Office Assistant', 'NOVATECH', 'Nairobi', 'contract', 'Our client, a leading company in the branding sector, is seeking to recruit a Receptionist/Front Office Assistant. The ideal candidate will be the first point of contact for visitors and clients, ensuring a welcoming and professional experience. This role requires excellent communication skills, strong organizational abilities, and the ability to multitask in a fast-paced environment.', '• Greet and welcome visitors in a friendly and professional manner.\r\n• Answer and direct phone calls, emails, and inquiries to the appropriate departments.\r\n• Manage front office operations, including handling correspondence and scheduling appointments.\r\n• Maintain a clean and organized reception area.\r\n• Assist with administrative tasks such as data entry, filing, and preparing reports.\r\n• Coordinate meetings, book conference rooms, and ensure meeting areas are set up appropriately.\r\n• Manage office supplies inventory and place orders as needed.\r\n• Receive and distribute mail, packages, and deliveries efficiently.\r\n• Support the sales and customer service teams by providing necessary information to clients.\r\n• Maintain records of visitors and ensure adherence to security and safety protocols.', '2025-04-12 08:38:42.997333', '2025-04-06', 'https://github.com/Felixngwono/Personal-Web', '37000-70000');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_jobapplication`
--

CREATE TABLE `storyteller_jobapplication` (
  `id` bigint(20) NOT NULL,
  `resume` varchar(100) DEFAULT NULL,
  `cover_letter` varchar(100) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `applied_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `job_id` bigint(20) NOT NULL,
  `applicant_name` varchar(100) DEFAULT NULL,
  `applicant_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_jobapplication`
--

INSERT INTO `storyteller_jobapplication` (`id`, `resume`, `cover_letter`, `status`, `applied_at`, `updated_at`, `job_id`, `applicant_name`, `applicant_id`) VALUES
(1, 'job_applications/resumes/KABARAK_UNIVERSITY.docx', 'Applicant\'s cover letter/image_demonstration.docx', 'under_review', '2025-04-07 14:20:48.198627', '2025-04-07 14:20:48.198627', 3, 'Felix Omondi', 1),
(2, 'job_applications/resumes/Bills_cv.pdf', 'Applicant\'s cover letter/Bills_cv.docx', 'under_review', '2025-04-12 16:47:15.832723', '2025-04-12 16:47:15.832859', 3, 'Felix Omondi', 5);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_message`
--

CREATE TABLE `storyteller_message` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `messaging` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_myuser`
--

CREATE TABLE `storyteller_myuser` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `bio` longtext DEFAULT NULL,
  `profilepic` varchar(100) NOT NULL,
  `birthdate` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `is_enduser` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_myuser`
--

INSERT INTO `storyteller_myuser` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `name`, `bio`, `profilepic`, `birthdate`, `gender`, `is_enduser`) VALUES
(1, 'pbkdf2_sha256$600000$Sg15T71IcMFGi2RySmPfq7$52+rQuX20wy4IDs31cF0Bz+C5gSggLmt58sHz8/K2mU=', '2025-08-04 17:24:55.511925', 0, 'Jakamolo', '', '', 'jakamolo@outlook.com', 0, 1, '2025-02-17 15:32:16.154366', NULL, NULL, 'profile_pics/24.jpg', '1990-10-23', 'male', 1),
(2, 'pbkdf2_sha256$600000$nBuSYDQMjfJTr8wh8prgzI$uoobDx1ug6/6iA45fNzJ9Fi+ZObmYi8bgN6O3cWBReY=', '2025-07-29 12:35:11.244390', 0, 'Salima', '', '', 'salima@gmail.com', 0, 1, '2025-02-19 10:22:55.502790', NULL, NULL, 'default.png', '1990-10-23', 'female', 1),
(3, 'pbkdf2_sha256$600000$L962lgx7bnmxKCdQDZuVao$TQPXCFywxIs/iVX8/w/xYSoHcV1c83hpZsPJt3nw32M=', '2025-07-29 12:31:47.878149', 0, 'Angie', '', '', 'angie@gmail.com', 0, 1, '2025-07-28 09:23:47.591845', 'Angela Valdes', NULL, 'default.png', NULL, 'female', 1),
(6, 'pbkdf2_sha256$600000$oqg3oFLGhFB90ZykAy4P3F$0o7HlO58KlGD3IopWHfX1yb/df9C5azEJU3Axlp0/Ow=', '2025-07-29 12:37:49.267646', 0, 'max', '', '', 'max@gmail.com', 0, 1, '2025-07-29 12:37:32.464488', 'carl Max', NULL, 'default.png', NULL, 'male', 0),
(8, 'pbkdf2_sha256$600000$UT6jaYlG7Jqp65UoyhnIOM$dEg5/HW0y6ExsPPztkp/rGLAIwIePguwQ8jjbiR+Ue0=', '2025-07-29 12:52:42.641396', 0, 'Wanjiku', '', '', 'faith@gmail.com', 0, 1, '2025-07-29 12:52:27.471243', 'Faith Wanjiku', NULL, 'avatar.png', NULL, 'male', 0),
(9, 'pbkdf2_sha256$600000$W82CLP2KyHBqElGLzX2Wnf$VDXG0EAUGE9M/9FY73sVMSYBoA9SsuFlCTwkjmPsA9o=', '2025-07-29 12:58:06.523841', 0, 'young', '', '', 'young@gmail.com', 0, 1, '2025-07-29 12:57:50.598915', 'Disney Onyango', NULL, 'avatar.png', NULL, 'male', 1),
(11, 'pbkdf2_sha256$600000$z4Ruy8VvHTbowCm9mp2t9M$BLEuF+5G4rmjfOPWGhjtF0dFQwNHNWEiXEjrANmt0d4=', '2025-08-05 10:12:42.929388', 1, 'FelloMarley', '', '', 'felixodhiambo@gmail.com', 1, 1, '2025-08-02 09:39:48.669872', 'Felix Odhiambo', 'im a software engineering', 'profiles/IMG_20250731_104429_1.jpg', NULL, 'male', 0);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_myuser_groups`
--

CREATE TABLE `storyteller_myuser_groups` (
  `id` bigint(20) NOT NULL,
  `myuser_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_myuser_user_permissions`
--

CREATE TABLE `storyteller_myuser_user_permissions` (
  `id` bigint(20) NOT NULL,
  `myuser_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_newslettersubscriber`
--

CREATE TABLE `storyteller_newslettersubscriber` (
  `id` bigint(20) NOT NULL,
  `email` varchar(254) NOT NULL,
  `subscribed_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_newslettersubscriber`
--

INSERT INTO `storyteller_newslettersubscriber` (`id`, `email`, `subscribed_at`) VALUES
(1, 'fellomarley@gmail.com', '2025-04-15 06:37:50.195975');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_notification`
--

CREATE TABLE `storyteller_notification` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `read` tinyint(1) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_notification`
--

INSERT INTO `storyteller_notification` (`id`, `title`, `description`, `created_at`, `read`, `user_id`) VALUES
(1, 'Innovation day at Kabarak University', 'Innovation day at Kabarak University', '2025-02-18 18:29:13.170608', 1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_portfolioitem`
--

CREATE TABLE `storyteller_portfolioitem` (
  `id` bigint(20) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `date_created` datetime(6) DEFAULT NULL,
  `author_id` bigint(20) DEFAULT NULL,
  `category` varchar(20) NOT NULL,
  `technology` varchar(2445) DEFAULT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_portfolioitem`
--

INSERT INTO `storyteller_portfolioitem` (`id`, `title`, `description`, `image`, `date_created`, `author_id`, `category`, `technology`, `video`) VALUES
(1, 'Building and shining of Kisumu', 'We dwealt in making Kisumu be a better place where investors and stakeholders can find to invest in.', 'portfolio_images/login.PNG', '2025-02-18 18:32:07.901293', 1, 'graphic', 'already structured devices', 'portfolio_videos/RATEGO_BABA_ENGLISH_TRANSLATION_-_MUSA_JUMA_NEW.mp4'),
(2, 'sewage removal in Dandora', 'There is urgent need to remove the wasres that are poluting environment in Dandora', 'portfolio_images/dandora_9xlf6Cb.jpg', '2025-02-18 18:33:02.106347', NULL, 'other', NULL, NULL),
(4, 'Government Tracking website', 'This website basically creates a platform where citizens can clearly track the following :\r\n\r\ni) All government projects including initiated, upcoming and completed projects\r\n\r\nii) Accountability of every government official \r\n\r\niii) Transpare in all government works', 'portfolio_images/judiciary.webp', '2025-02-18 18:35:47.722485', 1, 'other', 'django', 'portfolio_videos/mylivewallpapers.com-Nissan-GTR-Sports-Car_ir7uypC.mp4'),
(5, 'cherigat care foundation', 'We visited Cherigat care foundation to se how the kids were doing', 'portfolio_images/images_m5V7xsd.jpeg', '2025-02-18 18:36:49.617802', 1, 'other', 'Technology plays a crucial role in improving child care foundations by enhancing efficiency, education, health, and overall child welfare. Here are some key technologies used in child care foundations:  ### **1. Digital Record-Keeping & Management**   ✅ *', 'portfolio_videos/mylivewallpapers-com-Bugatti.mp4'),
(11, 'Tree planting day', 'will be hosting the president in our ground to help and mark the tree planting day', 'portfolio_images/tree.jpg', '2025-03-04 14:33:59.976252', 2, 'other', 'drones, cocoons, cultivator-planters, hydraulic excavators, apps, and seed pellets.', 'portfolio_videos/mylivewallpapers.com-Nissan-GTR-Sports-Car.mp4');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_project`
--

CREATE TABLE `storyteller_project` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `github_link` varchar(200) DEFAULT NULL,
  `live_demo` varchar(200) DEFAULT NULL,
  `technologies_used` varchar(255) DEFAULT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_project`
--

INSERT INTO `storyteller_project` (`id`, `title`, `description`, `image`, `github_link`, `live_demo`, `technologies_used`, `video`) VALUES
(2, 'Government Tracking website', 'The aim of this web was to try the oversee of the following:\r\n\r\ni) Tracking projects that th government ae working on\r\n\r\nii) Providing the accountability among governmnent officials\r\n\r\niii)user involvement in goverment works\r\n\r\niv) Providing Transparency in government works', 'project_images/Screenshot_2025-08-05_131400.png', 'https://github.com/Felixngwono/doverment--project.git', 'https://github.com/Felixngwono/FelloMarley.git', 'Python-Django', ''),
(3, 'Personal website', 'This is a personal project that tells the story of my life—my roots, my journey, my struggles, and my dreams. It\'s more than just a portfolio—it\'s a digital reflection of who I am. Through it, I share my family background, my educational path, the projects I\'ve worked on, and the lessons I\'ve learned along the way. My goal is to inspire others and leave a digital legacy that speaks not just of what I do, but who I truly am.\"', 'project_images/Screenshot_2025-08-05_131142.png', 'https://github.com/Felixngwono/personal-website.git', 'https://github.com/Felixngwono/personal-website.git', 'Python-Django, tailwind css, js and html', ''),
(4, 'loaning System', 'The Loaning System is a reliable platform designed to assist individuals in financial need by providing quick, secure, and accessible loan services. Whether you\'re seeking personal, emergency, or business support, our system allows you to request, track, and manage your loans with ease.', 'project_images/Screenshot_2025-08-05_132054.png', 'https://github.com/Felixngwono/Loaning-System', 'https://github.com/Felixngwono/Loaning-System', 'Python-Django, bootstrap css, js', '');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_sibling`
--

CREATE TABLE `storyteller_sibling` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `birthdate` date NOT NULL,
  `occupation` varchar(255) DEFAULT NULL,
  `short_description` longtext NOT NULL,
  `full_description` longtext NOT NULL,
  `profile_picture` varchar(100) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_sibling`
--

INSERT INTO `storyteller_sibling` (`id`, `name`, `birthdate`, `occupation`, `short_description`, `full_description`, `profile_picture`, `age`, `video`) VALUES
(1, 'Frankline Omondi', '0019-03-02', 'Pupil', 'Studying at Ratta Primary School.', 'Studying at Ratta Primary School. Wishing to pursue law in th future', 'siblings/avatar.png', 7, ''),
(2, 'Millicent Achieng', '1980-07-09', 'Business', 'A business woman in Kayaba-Nairobi', 'A business woman in Kayaba-Nairobi', 'siblings/about_0mlgfQV.jpg', 37, ''),
(3, 'Nancy Odhiambo', '2006-09-08', 'Student', 'im a high schooller at Ratta Secondary School', 'im Nancy Odhiambo, passionate in becoming a news anchor and a footballer', 'siblings/3006_JqayHev.webp', 19, ''),
(4, 'Kevin Odhiambo', '1990-06-07', 'Farming', 'small scale farming', 'small scale farming and also animal rearing', 'siblings/image_5.jpg', 35, ''),
(5, 'Winny Odhiambo', '1996-03-12', 'Business', 'working as a business girl in Kisumu', 'working as a business girl in Kisumu- Nyalenda', 'siblings/maxresdefault_LmrNR9s.jpg', 30, ''),
(6, 'Francis dhiambo', '1998-07-08', 'Student', 'Im a teacher by profession', 'A teacher by profession', 'siblings/bc4f9597d5a345fb919debbd4bbecced_bUCzfpB.jpg', 27, ''),
(7, 'Tonny Odhiambo', '1994-04-13', 'Engineer', 'Im a full stack software Developer', 'Im a full stack software Developer', 'siblings/person_2_XCk8YMl.jpg', 32, ''),
(8, 'Nicole Atieno', '2016-03-25', 'Student', 'student at Ratta primary', 'student at Ratta primary', 'siblings/Buore.JPG', 9, ''),
(9, 'Caroline Awuor', '1985-08-02', 'Farming', 'Large scale Farming', 'large scale farming', 'siblings/category-1.jpg', 40, '');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_siblingimage`
--

CREATE TABLE `storyteller_siblingimage` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `description` varchar(255) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `sibling_id` bigint(20) NOT NULL,
  `video` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_siblingimage`
--

INSERT INTO `storyteller_siblingimage` (`id`, `image`, `description`, `uploaded_at`, `sibling_id`, `video`) VALUES
(1, 'sibling_images/IMG_20231129_164813_1_aaLD3Mw.jpg', '', '2025-03-21 19:01:48.301159', 1, ''),
(2, 'sibling_images/25371f666f504419a3b77867cbf4a031_AAxXIbQ.jpg', '', '2025-03-21 19:02:37.252813', 3, ''),
(3, 'sibling_images/c5108994fa874ca4ba684ef987011239_8v1cqEH.jpg', '', '2025-03-21 19:02:57.881106', 3, ''),
(4, 'sibling_images/414ecbd4d8b74db7a55771b052e55150_WFPrVkn.jpg', '', '2025-03-21 19:03:26.244794', 5, ''),
(5, 'sibling_images/1f320bd56766414bba14f4fa36290b40_bUCjbul.jpg', '', '2025-03-21 19:03:42.050209', 5, ''),
(6, 'sibling_images/IMG_20240124_132402_suKOm30.jpg', '', '2025-03-21 19:04:16.224199', 7, ''),
(7, 'sibling_images/89ddd60d68c5437998ca1200e03d95f6_TCN5hQ9.jpg', '', '2025-03-21 19:04:57.793088', 6, ''),
(8, 'sibling_images/IMG_20250330_151627_1.jpg', '', '2025-04-15 16:03:57.546856', 1, ''),
(9, 'sibling_images/20230823_232505.jpg', '', '2025-04-15 16:07:36.130178', 1, '');

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_skill`
--

CREATE TABLE `storyteller_skill` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `proficiency` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_skill`
--

INSERT INTO `storyteller_skill` (`id`, `name`, `proficiency`) VALUES
(3, 'Football', 80),
(4, 'Python-django', 90),
(5, 'data science', 50),
(6, 'Tailwind. css/ Bootstrap.css', 80),
(7, 'React js', 50),
(8, 'Machine Learning', 50);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_support`
--

CREATE TABLE `storyteller_support` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `assignee_id` int(11) DEFAULT NULL,
  `attachment` varchar(100) DEFAULT NULL,
  `category` varchar(50) NOT NULL,
  `priority` varchar(10) NOT NULL,
  `status` varchar(15) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `resolution_notes` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_support`
--

INSERT INTO `storyteller_support` (`id`, `title`, `description`, `created_at`, `user_id`, `assignee_id`, `attachment`, `category`, `priority`, `status`, `updated_at`, `resolution_notes`) VALUES
(1, 'Home Suveilance', 'creating a CCTV surveilance to help in the scurity', '2025-02-28 17:40:58.142185', 1, NULL, 'support_attachments/LOGO.PNG', 'billing', 'medium', 'open', '2025-02-28 17:40:58.142185', NULL),
(2, 'Home Suveilance', 'creating a CCTV surveilance to help in the scurity', '2025-02-28 17:42:46.069175', 1, NULL, 'support_attachments/LOGO_JqDmQwv.PNG', 'billing', 'medium', 'open', '2025-02-28 17:42:46.069175', NULL),
(3, 'Home Suveilance', 'creating a CCTV surveilance to help in the scurity', '2025-02-28 17:43:33.105714', 1, NULL, 'support_attachments/LOGO_rW9J6pW.PNG', 'billing', 'medium', 'open', '2025-02-28 17:43:33.105714', NULL),
(4, 'gftryuiop', 'bjhjiuytrdffghjk', '2025-02-28 17:52:28.581892', 1, NULL, 'support_attachments/LOGO_lWPzlvP.PNG', 'other', 'medium', 'open', '2025-02-28 18:04:48.795162', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_task`
--

CREATE TABLE `storyteller_task` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `due_date` datetime(6) NOT NULL,
  `completed` tinyint(1) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `assigned_to_id` bigint(20) DEFAULT NULL,
  `created_by_id` bigint(20) NOT NULL,
  `priority` varchar(100) DEFAULT NULL,
  `progress_percentage` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_task`
--

INSERT INTO `storyteller_task` (`id`, `title`, `description`, `created_at`, `due_date`, `completed`, `completed_at`, `assigned_to_id`, `created_by_id`, `priority`, `progress_percentage`) VALUES
(1, 'Design Homepage UI', 'Create a modern and responsive homepage UI using Tailwind CSS, HTML and python-Django\r\n.', '2025-02-20 12:40:11.229622', '2025-01-29 00:00:00.000000', 0, '2025-04-10 00:00:00.000000', 1, 2, NULL, 50),
(2, 'gftryuijk', 'vcgfuhjnm', '2025-02-21 08:43:18.158702', '2025-02-28 00:00:00.000000', 0, '2025-04-10 00:00:00.000000', 1, 1, NULL, 50);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_testimonial`
--

CREATE TABLE `storyteller_testimonial` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `message` longtext NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_testimonial`
--

INSERT INTO `storyteller_testimonial` (`id`, `name`, `designation`, `message`, `image`, `created_at`, `user_id`) VALUES
(1, 'Assiello Nomar', 'Amanda Nicky', 'He\'s a capable man and always determined with his work. He works under minimal or even no supervision. I highly recommend him', 'testimonials/images.jpeg', '2025-03-04 09:52:25.340245', 1),
(2, 'Tonny Odhiambo', 'felix Odhiambo', 'Fello once said, \"Genious are never made from success nor failure but through hardwork \"', 'testimonials/pacho.jpg', '2025-03-04 14:55:47.607836', 1),
(3, 'Nancy Odhiambo', 'felix Odhiambo', 'My mentor, my role model, my supervisor. Always good at what he does', 'testimonials/Dr._Sarah_Tancredi.PNG', '2025-04-07 18:09:56.643437', 1);

-- --------------------------------------------------------

--
-- Table structure for table `storyteller_volunteer`
--

CREATE TABLE `storyteller_volunteer` (
  `id` bigint(20) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `availability` varchar(255) DEFAULT NULL,
  `skills` longtext DEFAULT NULL,
  `joined_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `reason` longtext DEFAULT NULL,
  `resume` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `storyteller_volunteer`
--

INSERT INTO `storyteller_volunteer` (`id`, `full_name`, `email`, `phone`, `availability`, `skills`, `joined_at`, `user_id`, `reason`, `resume`) VALUES
(1, 'Felix Odhiambo', 'jakamolo@outlook.com', '0723564897', NULL, '', '2025-03-05 20:00:46.012639', 4, 'nmghfty', 'resumes/Request-_It__Assistant.docx'),
(2, 'Amanda Vicky', 'amanda@gmail.com', '072456', NULL, 'web development', '2025-03-05 20:03:29.099754', 4, 'im driven by the position being done at this company. Im glad to bring my skills in the web development', 'resumes/Felixs_CV.pdf');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `storyteller_activity`
--
ALTER TABLE `storyteller_activity`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_activity_user_id_77738afa_fk_StoryTeller_myuser_id` (`user_id`);

--
-- Indexes for table `storyteller_blogpost`
--
ALTER TABLE `storyteller_blogpost`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_blogpost_author_id_7fb93907_fk_StoryTeller_myuser_id` (`author_id`);

--
-- Indexes for table `storyteller_certification`
--
ALTER TABLE `storyteller_certification`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_contact`
--
ALTER TABLE `storyteller_contact`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_donation`
--
ALTER TABLE `storyteller_donation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `transaction_id` (`transaction_id`),
  ADD KEY `StoryTeller_donation_donor_id_cd906040_fk_auth_user_id` (`donor_id`);

--
-- Indexes for table `storyteller_educationlevel`
--
ALTER TABLE `storyteller_educationlevel`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_event`
--
ALTER TABLE `storyteller_event`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_event_category_id_9b792a20_fk_StoryTell` (`category_id`),
  ADD KEY `StoryTeller_event_host_id_645f85b2_fk_StoryTeller_myuser_id` (`host_id`),
  ADD KEY `StoryTeller_event_location_id_8e3dba41_fk_StoryTell` (`location_id`);

--
-- Indexes for table `storyteller_eventcategory`
--
ALTER TABLE `storyteller_eventcategory`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_eventlocation`
--
ALTER TABLE `storyteller_eventlocation`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_faq`
--
ALTER TABLE `storyteller_faq`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_imagegallery`
--
ALTER TABLE `storyteller_imagegallery`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_job`
--
ALTER TABLE `storyteller_job`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_jobapplication`
--
ALTER TABLE `storyteller_jobapplication`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_jobapplication_job_id_a568f689_fk_StoryTeller_job_id` (`job_id`),
  ADD KEY `StoryTeller_jobapplication_applicant_id_066b7394_fk_auth_user_id` (`applicant_id`);

--
-- Indexes for table `storyteller_message`
--
ALTER TABLE `storyteller_message`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_myuser`
--
ALTER TABLE `storyteller_myuser`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `StoryTeller_myuser_email_a10080e3_uniq` (`email`);

--
-- Indexes for table `storyteller_myuser_groups`
--
ALTER TABLE `storyteller_myuser_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `StoryTeller_myuser_groups_myuser_id_group_id_179a3366_uniq` (`myuser_id`,`group_id`),
  ADD KEY `StoryTeller_myuser_groups_group_id_bd2ecf50_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `storyteller_myuser_user_permissions`
--
ALTER TABLE `storyteller_myuser_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `StoryTeller_myuser_user__myuser_id_permission_id_1eced865_uniq` (`myuser_id`,`permission_id`),
  ADD KEY `StoryTeller_myuser_u_permission_id_7727afc4_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `storyteller_newslettersubscriber`
--
ALTER TABLE `storyteller_newslettersubscriber`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `storyteller_notification`
--
ALTER TABLE `storyteller_notification`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_notifica_user_id_a521535c_fk_StoryTell` (`user_id`);

--
-- Indexes for table `storyteller_portfolioitem`
--
ALTER TABLE `storyteller_portfolioitem`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_portfoli_author_id_3bf72309_fk_StoryTell` (`author_id`);

--
-- Indexes for table `storyteller_project`
--
ALTER TABLE `storyteller_project`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_sibling`
--
ALTER TABLE `storyteller_sibling`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_siblingimage`
--
ALTER TABLE `storyteller_siblingimage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_siblingi_sibling_id_ee15fb4f_fk_StoryTell` (`sibling_id`);

--
-- Indexes for table `storyteller_skill`
--
ALTER TABLE `storyteller_skill`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `storyteller_support`
--
ALTER TABLE `storyteller_support`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_support_assignee_id_3e17786c_fk_auth_user_id` (`assignee_id`),
  ADD KEY `StoryTeller_support_user_id_7a170f6e_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `storyteller_task`
--
ALTER TABLE `storyteller_task`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_task_assigned_to_id_a96d8bc8_fk_StoryTell` (`assigned_to_id`),
  ADD KEY `StoryTeller_task_created_by_id_0d4966b1_fk_StoryTeller_myuser_id` (`created_by_id`);

--
-- Indexes for table `storyteller_testimonial`
--
ALTER TABLE `storyteller_testimonial`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_testimonial_user_id_745d5780_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `storyteller_volunteer`
--
ALTER TABLE `storyteller_volunteer`
  ADD PRIMARY KEY (`id`),
  ADD KEY `StoryTeller_volunteer_user_id_fc83d17b_fk_auth_user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=153;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT for table `storyteller_activity`
--
ALTER TABLE `storyteller_activity`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `storyteller_blogpost`
--
ALTER TABLE `storyteller_blogpost`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `storyteller_certification`
--
ALTER TABLE `storyteller_certification`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `storyteller_contact`
--
ALTER TABLE `storyteller_contact`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `storyteller_donation`
--
ALTER TABLE `storyteller_donation`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `storyteller_educationlevel`
--
ALTER TABLE `storyteller_educationlevel`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `storyteller_event`
--
ALTER TABLE `storyteller_event`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `storyteller_eventcategory`
--
ALTER TABLE `storyteller_eventcategory`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `storyteller_eventlocation`
--
ALTER TABLE `storyteller_eventlocation`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `storyteller_faq`
--
ALTER TABLE `storyteller_faq`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `storyteller_imagegallery`
--
ALTER TABLE `storyteller_imagegallery`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `storyteller_job`
--
ALTER TABLE `storyteller_job`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `storyteller_jobapplication`
--
ALTER TABLE `storyteller_jobapplication`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `storyteller_message`
--
ALTER TABLE `storyteller_message`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `storyteller_myuser`
--
ALTER TABLE `storyteller_myuser`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `storyteller_myuser_groups`
--
ALTER TABLE `storyteller_myuser_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `storyteller_myuser_user_permissions`
--
ALTER TABLE `storyteller_myuser_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `storyteller_newslettersubscriber`
--
ALTER TABLE `storyteller_newslettersubscriber`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `storyteller_notification`
--
ALTER TABLE `storyteller_notification`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `storyteller_portfolioitem`
--
ALTER TABLE `storyteller_portfolioitem`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `storyteller_project`
--
ALTER TABLE `storyteller_project`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `storyteller_sibling`
--
ALTER TABLE `storyteller_sibling`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `storyteller_siblingimage`
--
ALTER TABLE `storyteller_siblingimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `storyteller_skill`
--
ALTER TABLE `storyteller_skill`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `storyteller_support`
--
ALTER TABLE `storyteller_support`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `storyteller_task`
--
ALTER TABLE `storyteller_task`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `storyteller_testimonial`
--
ALTER TABLE `storyteller_testimonial`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `storyteller_volunteer`
--
ALTER TABLE `storyteller_volunteer`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `storyteller_activity`
--
ALTER TABLE `storyteller_activity`
  ADD CONSTRAINT `StoryTeller_activity_user_id_77738afa_fk_StoryTeller_myuser_id` FOREIGN KEY (`user_id`) REFERENCES `storyteller_myuser` (`id`);

--
-- Constraints for table `storyteller_blogpost`
--
ALTER TABLE `storyteller_blogpost`
  ADD CONSTRAINT `StoryTeller_blogpost_author_id_7fb93907_fk_StoryTeller_myuser_id` FOREIGN KEY (`author_id`) REFERENCES `storyteller_myuser` (`id`);

--
-- Constraints for table `storyteller_donation`
--
ALTER TABLE `storyteller_donation`
  ADD CONSTRAINT `StoryTeller_donation_donor_id_cd906040_fk_auth_user_id` FOREIGN KEY (`donor_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `storyteller_event`
--
ALTER TABLE `storyteller_event`
  ADD CONSTRAINT `StoryTeller_event_category_id_9b792a20_fk_StoryTell` FOREIGN KEY (`category_id`) REFERENCES `storyteller_eventcategory` (`id`),
  ADD CONSTRAINT `StoryTeller_event_host_id_645f85b2_fk_StoryTeller_myuser_id` FOREIGN KEY (`host_id`) REFERENCES `storyteller_myuser` (`id`),
  ADD CONSTRAINT `StoryTeller_event_location_id_8e3dba41_fk_StoryTell` FOREIGN KEY (`location_id`) REFERENCES `storyteller_eventlocation` (`id`);

--
-- Constraints for table `storyteller_jobapplication`
--
ALTER TABLE `storyteller_jobapplication`
  ADD CONSTRAINT `StoryTeller_jobapplication_applicant_id_066b7394_fk_auth_user_id` FOREIGN KEY (`applicant_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `StoryTeller_jobapplication_job_id_a568f689_fk_StoryTeller_job_id` FOREIGN KEY (`job_id`) REFERENCES `storyteller_job` (`id`);

--
-- Constraints for table `storyteller_myuser_groups`
--
ALTER TABLE `storyteller_myuser_groups`
  ADD CONSTRAINT `StoryTeller_myuser_g_myuser_id_8ccd8420_fk_StoryTell` FOREIGN KEY (`myuser_id`) REFERENCES `storyteller_myuser` (`id`),
  ADD CONSTRAINT `StoryTeller_myuser_groups_group_id_bd2ecf50_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `storyteller_myuser_user_permissions`
--
ALTER TABLE `storyteller_myuser_user_permissions`
  ADD CONSTRAINT `StoryTeller_myuser_u_myuser_id_fa5b802f_fk_StoryTell` FOREIGN KEY (`myuser_id`) REFERENCES `storyteller_myuser` (`id`),
  ADD CONSTRAINT `StoryTeller_myuser_u_permission_id_7727afc4_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);

--
-- Constraints for table `storyteller_notification`
--
ALTER TABLE `storyteller_notification`
  ADD CONSTRAINT `StoryTeller_notifica_user_id_a521535c_fk_StoryTell` FOREIGN KEY (`user_id`) REFERENCES `storyteller_myuser` (`id`);

--
-- Constraints for table `storyteller_portfolioitem`
--
ALTER TABLE `storyteller_portfolioitem`
  ADD CONSTRAINT `StoryTeller_portfoli_author_id_3bf72309_fk_StoryTell` FOREIGN KEY (`author_id`) REFERENCES `storyteller_myuser` (`id`);

--
-- Constraints for table `storyteller_siblingimage`
--
ALTER TABLE `storyteller_siblingimage`
  ADD CONSTRAINT `StoryTeller_siblingi_sibling_id_ee15fb4f_fk_StoryTell` FOREIGN KEY (`sibling_id`) REFERENCES `storyteller_sibling` (`id`);

--
-- Constraints for table `storyteller_support`
--
ALTER TABLE `storyteller_support`
  ADD CONSTRAINT `StoryTeller_support_assignee_id_3e17786c_fk_auth_user_id` FOREIGN KEY (`assignee_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `StoryTeller_support_user_id_7a170f6e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `storyteller_task`
--
ALTER TABLE `storyteller_task`
  ADD CONSTRAINT `StoryTeller_task_assigned_to_id_a96d8bc8_fk_StoryTell` FOREIGN KEY (`assigned_to_id`) REFERENCES `storyteller_myuser` (`id`),
  ADD CONSTRAINT `StoryTeller_task_created_by_id_0d4966b1_fk_StoryTeller_myuser_id` FOREIGN KEY (`created_by_id`) REFERENCES `storyteller_myuser` (`id`);

--
-- Constraints for table `storyteller_testimonial`
--
ALTER TABLE `storyteller_testimonial`
  ADD CONSTRAINT `StoryTeller_testimonial_user_id_745d5780_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `storyteller_volunteer`
--
ALTER TABLE `storyteller_volunteer`
  ADD CONSTRAINT `StoryTeller_volunteer_user_id_fc83d17b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
