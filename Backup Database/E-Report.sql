USE [master]
GO
/****** Object:  Database [E-Report]    Script Date: 10/16/2024 4:33:16 PM ******/
CREATE DATABASE [E-Report]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'E-Report', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\E-Report.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'E-Report_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\E-Report_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT
GO
ALTER DATABASE [E-Report] SET COMPATIBILITY_LEVEL = 150
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [E-Report].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [E-Report] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [E-Report] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [E-Report] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [E-Report] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [E-Report] SET ARITHABORT OFF 
GO
ALTER DATABASE [E-Report] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [E-Report] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [E-Report] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [E-Report] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [E-Report] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [E-Report] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [E-Report] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [E-Report] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [E-Report] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [E-Report] SET  DISABLE_BROKER 
GO
ALTER DATABASE [E-Report] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [E-Report] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [E-Report] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [E-Report] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [E-Report] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [E-Report] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [E-Report] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [E-Report] SET RECOVERY SIMPLE 
GO
ALTER DATABASE [E-Report] SET  MULTI_USER 
GO
ALTER DATABASE [E-Report] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [E-Report] SET DB_CHAINING OFF 
GO
ALTER DATABASE [E-Report] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [E-Report] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [E-Report] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [E-Report] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
ALTER DATABASE [E-Report] SET QUERY_STORE = OFF
GO
USE [E-Report]
GO
/****** Object:  User [E-Report]    Script Date: 10/16/2024 4:33:16 PM ******/
CREATE USER [E-Report] FOR LOGIN [E-Report] WITH DEFAULT_SCHEMA=[dbo]
GO
ALTER ROLE [db_owner] ADD MEMBER [E-Report]
GO
ALTER ROLE [db_accessadmin] ADD MEMBER [E-Report]
GO
ALTER ROLE [db_ddladmin] ADD MEMBER [E-Report]
GO
ALTER ROLE [db_datareader] ADD MEMBER [E-Report]
GO
ALTER ROLE [db_datawriter] ADD MEMBER [E-Report]
GO
/****** Object:  Table [dbo].[Permissions]    Script Date: 10/16/2024 4:33:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Permissions](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[email] [nvarchar](100) NOT NULL,
	[addButton] [nvarchar](10) NULL,
	[editButton] [nvarchar](10) NULL,
	[manageButton] [nvarchar](10) NULL,
	[publishButton] [nvarchar](10) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Reports]    Script Date: 10/16/2024 4:33:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Reports](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](100) NOT NULL,
	[group_id] [nvarchar](100) NOT NULL,
	[report_id] [nvarchar](100) NOT NULL,
	[refresh_frequency] [nvarchar](100) NULL,
	[refresh_frequency_value] [int] NOT NULL,
	[refresh_frequency_unit] [varchar](10) NOT NULL,
	[icon_path] [varchar](200) NOT NULL,
	[dataset_id] [nvarchar](100) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[session]    Script Date: 10/16/2024 4:33:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[session](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[expiration] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[sessions]    Script Date: 10/16/2024 4:33:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[sessions](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[session_id] [varchar](255) NULL,
	[data] [varbinary](max) NULL,
	[expiry] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[session_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Settings]    Script Date: 10/16/2024 4:33:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Settings](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[key] [nvarchar](100) NOT NULL,
	[value] [nvarchar](500) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Users]    Script Date: 10/16/2024 4:33:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[workday_id] [nvarchar](100) NOT NULL,
	[employee_chi_name] [nvarchar](100) NOT NULL,
	[employee_last_name] [nvarchar](100) NOT NULL,
	[employee_first_name] [nvarchar](100) NOT NULL,
	[work_email] [nvarchar](100) NOT NULL,
	[ntid] [nvarchar](100) NOT NULL,
	[employee_workcell] [nvarchar](100) NOT NULL,
	[department_name] [nvarchar](100) NOT NULL,
	[direct_manager] [nvarchar](100) NOT NULL,
	[direct_manager_wdid] [nvarchar](100) NOT NULL,
	[direct_manager_email] [nvarchar](100) NOT NULL,
	[direct_manager_ntid] [nvarchar](100) NOT NULL,
	[company_code] [nvarchar](100) NOT NULL,
	[company_location] [nvarchar](100) NOT NULL,
	[job_family_group] [nvarchar](100) NOT NULL,
	[business_title] [nvarchar](100) NOT NULL,
	[cost_center_id] [nvarchar](100) NOT NULL,
	[global_job_title] [nvarchar](100) NOT NULL,
	[employee_nationality] [nvarchar](100) NOT NULL,
	[password] [nvarchar](100) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Users]  WITH NOCHECK ADD  CONSTRAINT [FK_Users_Permissions] FOREIGN KEY([id])
REFERENCES [dbo].[Permissions] ([id])
GO
ALTER TABLE [dbo].[Users] CHECK CONSTRAINT [FK_Users_Permissions]
GO
USE [master]
GO
ALTER DATABASE [E-Report] SET  READ_WRITE 
GO
