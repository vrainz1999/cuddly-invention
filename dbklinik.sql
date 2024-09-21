-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 21, 2024 at 02:37 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dbklinik`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('0779eb09aed9');

-- --------------------------------------------------------

--
-- Table structure for table `dokter`
--

CREATE TABLE `dokter` (
  `id` int(11) NOT NULL,
  `nama` varchar(150) DEFAULT NULL,
  `jadwal` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `dokter`
--

INSERT INTO `dokter` (`id`, `nama`, `jadwal`) VALUES
(11, 'Dr. Ridwan', 'Senin-Saptu: 13:00-16:50 WIB'),
(16, 'Dr. Vina', 'Jumat & Saptu 17:00-selesai');

-- --------------------------------------------------------

--
-- Table structure for table `obat`
--

CREATE TABLE `obat` (
  `id` int(11) NOT NULL,
  `namaObat` varchar(150) DEFAULT NULL,
  `jenisObat` varchar(150) DEFAULT NULL,
  `harga_beli` int(11) DEFAULT NULL,
  `harga_jual` int(11) DEFAULT NULL,
  `suplier_id` int(11) DEFAULT NULL,
  `kondisi` varchar(80) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `obat`
--

INSERT INTO `obat` (`id`, `namaObat`, `jenisObat`, `harga_beli`, `harga_jual`, `suplier_id`, `kondisi`) VALUES
(8, 'Panadol', 'Psitropika', 6000, 3000, 1, 'Baik'),
(10, 'Bodrek', 'Paten', 10000, 12000, 6, 'Rusak'),
(13, 'Omeprazole', 'Paten', 12000, 15000, 1, 'Baik'),
(15, 'Paramex', 'Paten', 5000, 7000, 7, 'Baik');

-- --------------------------------------------------------

--
-- Table structure for table `pasien`
--

CREATE TABLE `pasien` (
  `id` bigint(20) NOT NULL,
  `nama` varchar(150) DEFAULT NULL,
  `keluhan` text DEFAULT NULL,
  `diagnosa` varchar(100) DEFAULT NULL,
  `resep` text DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `pendaftaran_id` bigint(20) DEFAULT NULL,
  `tanggal` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pasien`
--

INSERT INTO `pasien` (`id`, `nama`, `keluhan`, `diagnosa`, `resep`, `user_id`, `pendaftaran_id`, `tanggal`) VALUES
(2, 'Agus', 'Panas', 'Radang', 'Ibufroven 1x3', 9, NULL, '18 September 2024 Jam 19:09:14'),
(3, 'Yusuf', 'Sakit Kepala', 'Tekanan Darah Tinggi', 'Amlodipine Hexpharm 3x', 9, NULL, '18 September 2024 Jam 20:26:20');

-- --------------------------------------------------------

--
-- Table structure for table `pendaftaran`
--

CREATE TABLE `pendaftaran` (
  `id` bigint(20) NOT NULL,
  `nama` varchar(150) DEFAULT NULL,
  `tl` varchar(100) DEFAULT NULL,
  `tg_lahir` varchar(100) DEFAULT NULL,
  `jk` varchar(100) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `profesi` varchar(100) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `keterangan` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pendaftaran`
--

INSERT INTO `pendaftaran` (`id`, `nama`, `tl`, `tg_lahir`, `jk`, `status`, `profesi`, `alamat`, `keterangan`) VALUES
(69, 'Yuni', 'Surabaya', '2018-01-02', 'Perempuan', 'Belum Menikah', 'Mahasiswa', 'Jl. Waru12', 'Diproses'),
(71, 'Yuli', 'Jombang', '2024-09-19', 'Perempuan', 'Sudah Menikah', 'Ibu Rumah Tangga', 'Jl. Griya Santa 2', 'Diproses');

-- --------------------------------------------------------

--
-- Table structure for table `suplier`
--

CREATE TABLE `suplier` (
  `id` int(11) NOT NULL,
  `perusahaan` varchar(200) DEFAULT NULL,
  `kontak` varchar(100) DEFAULT NULL,
  `alamat` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `suplier`
--

INSERT INTO `suplier` (`id`, `perusahaan`, `kontak`, `alamat`) VALUES
(1, 'PT Kimia Farma', '081222111', 'Jl. Garuda'),
(6, 'PT Sido Muncul', '081222111', 'Jl. Fatmawati'),
(7, 'PT Arga Jaya', '08155544444', 'Jl. PENARUKAN bANTEN'),
(8, 'PT Agung', '081667772222', 'Jl. Jombang');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(150) DEFAULT NULL,
  `password` text DEFAULT NULL,
  `level` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `username`, `password`, `level`) VALUES
(2, 'Admin', '$2b$12$nBK1c1fKcUR8AoV53P/lE.JNeMjVpKM4fcwkHqcwrwVvQibECdhSm', 'Admin'),
(6, 'Agus Purnawan', '$2b$12$oQxEQTHUJgQfOkSfIy1xweAmGzE2qc2O2uTOswnjeyO6LtjKayMZq', 'Administrasi'),
(9, 'Dr.Ridwan', '$2b$12$NxsQ8Aoe6/N.crudZL6hqe/VvA0tU3UTYy5TpU5ATLy8DUNwafjyu', 'Dokter'),
(10, 'Admin', '$2b$12$kvWMlFc1FxWS046MMdX0reR5OXHzdeqvIewDxaVvhL.Y/3WEGOpn.', 'Admin');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `dokter`
--
ALTER TABLE `dokter`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `obat`
--
ALTER TABLE `obat`
  ADD PRIMARY KEY (`id`),
  ADD KEY `suplier_id` (`suplier_id`);

--
-- Indexes for table `pasien`
--
ALTER TABLE `pasien`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `pendaftaran_id` (`pendaftaran_id`);

--
-- Indexes for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `suplier`
--
ALTER TABLE `suplier`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `dokter`
--
ALTER TABLE `dokter`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `obat`
--
ALTER TABLE `obat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `pasien`
--
ALTER TABLE `pasien`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=72;

--
-- AUTO_INCREMENT for table `suplier`
--
ALTER TABLE `suplier`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `obat`
--
ALTER TABLE `obat`
  ADD CONSTRAINT `obat_ibfk_1` FOREIGN KEY (`suplier_id`) REFERENCES `suplier` (`id`);

--
-- Constraints for table `pasien`
--
ALTER TABLE `pasien`
  ADD CONSTRAINT `pasien_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `pasien_ibfk_2` FOREIGN KEY (`pendaftaran_id`) REFERENCES `pendaftaran` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
