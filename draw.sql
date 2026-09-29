/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50744
 Source Host           : localhost:3306
 Source Schema         : pulse

 Target Server Type    : MySQL
 Target Server Version : 50744
 File Encoding         : 65001

 Date: 29/09/2026 17:26:02
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for draw
-- ----------------------------
DROP TABLE IF EXISTS `draw`;
CREATE TABLE `draw`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `draw_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '抽奖名称',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态 1:未开始 2:进行中 3:已结束 4:已下线',
  `start_time` datetime NULL DEFAULT NULL COMMENT '抽奖开始时间',
  `offline_time` datetime NULL DEFAULT NULL COMMENT '抽奖下线时间',
  `desc` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '抽奖描述',
  `op_id` bigint(20) NULL DEFAULT NULL COMMENT '创建人user_id',
  `up_id` bigint(20) NULL DEFAULT NULL COMMENT '更新人user_id',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10003 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '抽奖活动' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for draw_prize
-- ----------------------------
DROP TABLE IF EXISTS `draw_prize`;
CREATE TABLE `draw_prize`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `draw_id` int(11) NOT NULL DEFAULT 0 COMMENT '抽奖活动id',
  `prize_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖品名称',
  `prize_sku` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖品唯一标识',
  `prize_type` tinyint(4) NOT NULL DEFAULT 0 COMMENT '奖品类型 1:实物 2:优惠券',
  `is_guaranteed` tinyint(4) NOT NULL DEFAULT 0 COMMENT '是否兜底 0:否 1:是',
  `prize_price` int(11) NOT NULL DEFAULT 0 COMMENT '奖品价格(分)',
  `prize_inventory` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '奖品库存',
  `draw_prize_status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '奖品状态 （1:上架，2:下架）',
  `reduce_inventory` int(11) UNSIGNED NOT NULL DEFAULT 0 COMMENT '已消耗库存',
  `prize_picture` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '奖品图片',
  `probability` int(11) NOT NULL DEFAULT 0 COMMENT '奖品概率(万分比 0-10000)',
  `op_id` bigint(20) NULL DEFAULT NULL COMMENT '创建人user_id',
  `up_id` bigint(20) NULL DEFAULT NULL COMMENT '更新人user_id',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_draw_id`(`draw_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '奖品配置' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for prize
-- ----------------------------
DROP TABLE IF EXISTS `prize`;
CREATE TABLE `prize`  (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '奖品主键ID',
  `prize_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖品名称',
  `brand` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '品牌',
  `prize_sku` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖品sku',
  `prize_type` tinyint(4) NOT NULL COMMENT '奖品类型：1实物 2虚拟卡券 3现金红包 4其他',
  `color` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '奖品颜色',
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '主图（快速展示用）',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '奖品描述/兑换说明',
  `cost_price` decimal(10, 2) NULL DEFAULT NULL COMMENT '成本价',
  `market_price` decimal(10, 2) NULL DEFAULT NULL COMMENT '市场价（展示用）',
  `total_stock` int(11) NOT NULL DEFAULT 0 COMMENT '总库存',
  `remaining_stock` int(11) NOT NULL DEFAULT 0 COMMENT '剩余库存',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1上架 2下架',
  `op_id` bigint(20) NULL DEFAULT NULL COMMENT '创建人user_id',
  `up_id` bigint(20) NULL DEFAULT NULL COMMENT '更新人user_id',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_type`(`prize_type`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  INDEX `idx_prize_sku`(`prize_sku`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '奖品表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for requirement
-- ----------------------------
DROP TABLE IF EXISTS `requirement`;
CREATE TABLE `requirement`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `req_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '需求id',
  `req_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '需求名称',
  `product_users` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '产品人员(user_id逗号分隔)',
  `dev_users` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '开发人员(user_id逗号分隔)',
  `test_users` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '测试人员(user_id逗号分隔)',
  `dev_start_time` datetime NULL DEFAULT NULL COMMENT '研发开始时间',
  `dev_end_time` datetime NULL DEFAULT NULL COMMENT '研发结束时间',
  `test_start_time` datetime NULL DEFAULT NULL COMMENT '测试开始时间',
  `test_end_time` datetime NULL DEFAULT NULL COMMENT '测试结束时间',
  `online_time` datetime NULL DEFAULT NULL COMMENT '上线时间',
  `skip_test` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否免测 0否 1是',
  `requester` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '需求方',
  `op_id` bigint(20) NULL DEFAULT NULL COMMENT '创建人user_id',
  `up_id` bigint(20) NULL DEFAULT NULL COMMENT '更新人user_id',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_req_id`(`req_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '需求表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户id',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '密码',
  `status` int(11) NOT NULL DEFAULT 1 COMMENT '类型:1代表正常, 2代表禁用, 3代表注销',
  `created_time` datetime(6) NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_time` datetime(6) NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_username`(`username`) USING BTREE,
  UNIQUE INDEX `idx_user_id`(`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_draw
-- ----------------------------
DROP TABLE IF EXISTS `user_draw`;
CREATE TABLE `user_draw`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint(20) NOT NULL COMMENT '用户id',
  `draw_id` int(11) NOT NULL DEFAULT 0 COMMENT '抽奖活动id',
  `total_quota` int(11) NOT NULL DEFAULT 0 COMMENT '抽奖次数',
  `used_times` int(11) NOT NULL DEFAULT 0 COMMENT '已使用次数',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_draw`(`user_id`, `draw_id`) USING BTREE,
  INDEX `idx_draw_id`(`draw_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户抽奖次数' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_draw_log
-- ----------------------------
DROP TABLE IF EXISTS `user_draw_log`;
CREATE TABLE `user_draw_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint(20) NOT NULL COMMENT '用户id',
  `draw_id` int(11) NOT NULL DEFAULT 0 COMMENT '抽奖活动id',
  `draw_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '抽奖时间',
  `is_win` tinyint(4) NOT NULL DEFAULT 0 COMMENT '是否中奖：0-未中，1-中奖',
  `prize_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖品名称',
  `prize_sku` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖品sku',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_draw_id`(`draw_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户抽奖日志' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_draw_prize
-- ----------------------------
DROP TABLE IF EXISTS `user_draw_prize`;
CREATE TABLE `user_draw_prize`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint(20) NOT NULL COMMENT '用户id',
  `draw_id` int(11) NOT NULL DEFAULT 0 COMMENT '抽奖活动id',
  `draw_prize_id` int(11) NOT NULL DEFAULT 0 COMMENT '奖品配置id',
  `prize_sku` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '奖品唯一标识',
  `status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '领奖状态 0:未领取 1:已领取 2:已过期',
  `draw_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '抽奖时间',
  `claim_time` datetime NULL DEFAULT NULL COMMENT '领取时间',
  `expire_time` datetime NULL DEFAULT NULL COMMENT '过期时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_draw_id`(`draw_id`) USING BTREE,
  INDEX `idx_prize_id`(`draw_prize_id`) USING BTREE,
  INDEX `idx_prize_sku`(`prize_sku`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户获奖记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_info
-- ----------------------------
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名称',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户头像',
  `sex` int(11) NULL DEFAULT 0 COMMENT '性别:1代表男, 2代表女',
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '详细居住地址',
  `phone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '手机号',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '邮箱',
  `wechat` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '微信号',
  `user_id` bigint(20) NOT NULL COMMENT '关联用户id',
  `desc` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '个人简介',
  `created_time` datetime(6) NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_time` datetime(6) NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_login_log
-- ----------------------------
DROP TABLE IF EXISTS `user_login_log`;
CREATE TABLE `user_login_log`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `user_id` bigint(20) NOT NULL COMMENT '用户id',
  `ip` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '登录IP',
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备名称，如\"iPhone 15\" / \"Chrome on Windows\"',
  `device_type` tinyint(4) NULL DEFAULT NULL COMMENT '设备类型：1:pc 2:app 3:ipad',
  `os` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '操作系统，如\"Windows 10\" / \"iOS 17\"',
  `login_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '登录时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_login_time`(`login_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 40 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户登录日志表' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
