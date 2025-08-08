# coding: utf8
import os
import numpy as np
import SimpleITK as sitk

def get_volumer(file_type=''):
    if file_type.lower() == 'dicom':
        runner = DicomVolumer()
    elif file_type.lower() == 'nii':
        runner = NiiVolumer()
    else:
        raise ValueError('Invalid file type')
    return runner

class Volumer:
    runner = None
    def __init__(self):
        pass

    def get_volume(self, source, roi, label_values=None):
        return self.runner.get_volume(source, roi)

    def _load_nifti_image(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        image = sitk.ReadImage(file_path)
        return image

    def _resample_mask_to_image(self, mask, reference_image):
        """
        将掩膜重采样到参考图像的空间坐标系
        :param mask: 要重采样的掩膜图像
        :param reference_image: 参考图像 (DICOM图像)
        :return: 重采样后的掩膜图像
        """
        # 检查是否需要重采样
        if (mask.GetSize() == reference_image.GetSize() and
                mask.GetSpacing() == reference_image.GetSpacing() and
                mask.GetOrigin() == reference_image.GetOrigin() and
                mask.GetDirection() == reference_image.GetDirection()):
            print("掩膜已与DICOM图像对齐，无需重采样")
            return mask

        # 设置重采样器
        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(reference_image)
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)  # 最近邻插值，保持标签值不变
        resampler.SetOutputPixelType(mask.GetPixelID())

        # 执行重采样
        resampled_mask = resampler.Execute(mask)
        return resampled_mask


class NiiVolumer(Volumer):

    def get_volume(self, nii_path, roi_path, label_values=None):
        ct_images = self._load_nifti_image(nii_path)
        mask_image = self._load_nifti_image(roi_path)
        # 将掩膜转换为NumPy数组
        resampled_mask_image = self._resample_mask_to_image(mask_image, ct_images)
        mask_array = sitk.GetArrayFromImage(resampled_mask_image)  # 维度顺序: (z, y, x)

        # 计算体积
        spacing = ct_images.GetSpacing()
        voxel_volume = spacing[0] * spacing[1] * spacing[2] # 计算单个体素的体积
        roi_volume = sitk.GetArrayFromImage(mask_image).sum() * voxel_volume # 计算总体积

        # 确定要计算的标签
        if label_values is None:
            # 获取所有非零标签
            label_values = np.unique(mask_array)
            label_values = label_values[label_values != 0]

        if len(label_values) == 0:
            raise ValueError("警告: 掩膜中没有非零标签!")

        # 计算每个标签的体积
        volumes = {}
        for label in label_values:
            voxel_count = np.sum(mask_array == label)
            volume_mm3 = voxel_count * voxel_volume
            volumes[label] = {
                'voxel_count': voxel_count,
                'volume_mm3': volume_mm3,
                'volume_cm3': volume_mm3 / 1000.0,
                'volume_ml': volume_mm3 / 1000.0  # 1 cm³ = 1 mL
            }
            print(f"标签 {label}: {voxel_count}个体素, {volume_mm3:.2f} mm³ ({volume_mm3 / 1000:.2f} cm³)")

        return volumes


class DicomVolumer(Volumer):

    def get_volume(self, dicom_dir, roi, label_values=None):
        ct_images = self._load_dicom_images(dicom_dir)
        mask_image = self._load_nifti_image(roi)
        resampled_mask_image = self._resample_mask_to_image(mask_image, ct_images)

        """
            计算掩膜中指定标签的体积
            :param image: DICOM图像 (用于获取空间信息)
            :param mask: 掩膜图像
            :param label_values: 要计算体积的标签值列表 (None表示所有非零标签)
            :return: 体积字典 {标签值: 体积(mm³)}
            """
        # 获取体素间距 (使用DICOM图像的空间信息)
        spacing = ct_images.GetSpacing()
        voxel_volume = spacing[0] * spacing[1] * spacing[2]  # mm³

        # 将掩膜转换为NumPy数组
        mask_array = sitk.GetArrayFromImage(resampled_mask_image)  # 维度顺序: (z, y, x)

        # 确定要计算的标签
        if label_values is None:
            # 获取所有非零标签
            label_values = np.unique(mask_array)
            label_values = label_values[label_values != 0]

        if len(label_values) == 0:
            raise ValueError("警告: 掩膜中没有非零标签!")

        # 计算每个标签的体积
        volumes = {}
        for label in label_values:
            voxel_count = np.sum(mask_array == label)
            volume_mm3 = voxel_count * voxel_volume
            volumes[label] = {
                'voxel_count': voxel_count,
                'volume_mm3': volume_mm3,
                'volume_cm3': volume_mm3 / 1000.0,
                'volume_ml': volume_mm3 / 1000.0  # 1 cm³ = 1 mL
            }
            # print(f"标签 {label}: {voxel_count}个体素, {volume_mm3:.2f} mm³ ({volume_mm3 / 1000:.2f} cm³)")

        return volumes

    def _load_dicom_images(self, dicom_dir):
        dicom_dir = os.path.abspath(os.path.expanduser(dicom_dir))
        # 加载dicom目录
        reader = sitk.ImageSeriesReader()
        # 获取DICOM序列的文件名
        dicom_files = reader.GetGDCMSeriesFileNames(dicom_dir)
        if not dicom_files:
            raise FileNotFoundError(f"在目录 {dicom_dir} 中未找到DICOM文件")
        reader.SetFileNames(dicom_files)
        ct_images = reader.Execute()
        return ct_images
