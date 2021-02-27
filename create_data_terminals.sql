CREATE TABLE `data_terminals` (
  `SW(Switch Lable)` text,
  `T1(Terminal 1)` bigint DEFAULT NULL,
  `T2(Terminal 2)` bigint DEFAULT NULL,
  `T3(Terminal 3)` bigint DEFAULT NULL,
  `T4(Terminal 4)` bigint DEFAULT NULL,
  `T5(Terminal 5)` bigint DEFAULT NULL,
  `TS(Unix Timestamp)` bigint DEFAULT NULL,
  `switch` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
