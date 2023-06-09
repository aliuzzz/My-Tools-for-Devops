/*
 Navicat Premium Data Transfer

 Source Server         : 47.94.86.144_3306
 Source Server Type    : MySQL
 Source Server Version : 80026
 Source Host           : 47.94.86.144:3306
 Source Schema         : mtr

 Target Server Type    : MySQL
 Target Server Version : 80026
 File Encoding         : 65001

 Date: 09/06/2023 14:09:05
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for mtr_company
-- ----------------------------
DROP TABLE IF EXISTS `mtr_company`;
CREATE TABLE `mtr_company`  (
  `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `ip` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `region` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `room` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `custom` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `operator` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 165 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of mtr_company
-- ----------------------------
INSERT INTO `mtr_company` VALUES (1, '192.168.1.2', '东北-辽宁', '大连电信', '客户1', '运营商1', '大连电信-192.168.1.2-客户1-运营商1');
INSERT INTO `mtr_company` VALUES (2, '192.168.5.101', '华北-山东', '济南电信', '客户2', '运营商2', '济南电信-192.168.5.101-客户2-运营商2');

SET FOREIGN_KEY_CHECKS = 1;
