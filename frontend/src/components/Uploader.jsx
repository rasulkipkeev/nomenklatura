import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, X, CheckCircle } from 'lucide-react';
import axios from 'axios';

export function Uploader({ onUploadSuccess }) {
    const [file, setFile] = useState(null);
    const [supplierName, setSupplierName] = useState('');
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');

    const onDrop = useCallback((acceptedFiles) => {
        setError('');
        const selected = acceptedFiles[0];
        if (selected) {
            const ext = selected.name.split('.').pop().toLowerCase();
            if (!['csv', 'xlsx', 'xls', 'xml'].includes(ext)) {
                setError('Неподдерживаемый формат файла. Загрузите .csv, .xlsx или .xml');
                return;
            }
            setFile(selected);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        maxFiles: 1,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls'],
            'text/xml': ['.xml']
        }
    });

    const handleUpload = async () => {
        if (!file || !supplierName.trim()) {
            setError('Укажите имя поставщика и выберите файл');
            return;
        }

        setUploading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('supplier_name', supplierName);

        try {
            await axios.post('http://localhost:8000/api/upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Auto-trigger match after upload
            await axios.post('http://localhost:8000/api/match/');

            setFile(null);
            setSupplierName('');
            if (onUploadSuccess) onUploadSuccess();

        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка при загрузке файла');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 max-w-2xl w-full mx-auto">
            <h2 className="text-xl font-semibold mb-4 text-slate-800">Загрузка прайс-листа</h2>

            <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">
                    Название поставщика
                </label>
                <input
                    type="text"
                    value={supplierName}
                    onChange={(e) => setSupplierName(e.target.value)}
                    placeholder="Например: ООО Ромашка"
                    className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                />
            </div>

            {!file ? (
                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ease-in-out
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}`}
                >
                    <input {...getInputProps()} />
                    <UploadCloud className={`mx-auto h-12 w-12 mb-4 ${isDragActive ? 'text-blue-500' : 'text-slate-400'}`} />
                    <p className="text-slate-600 font-medium mb-1">
                        {isDragActive ? 'Отпустите файл здесь' : 'Перетащите файл сюда или нажмите для выбора'}
                    </p>
                    <p className="text-sm text-slate-500">
                        Поддерживаются форматы: .xlsx, .csv, .xml
                    </p>
                </div>
            ) : (
                <div className="bg-blue-50 rounded-lg p-4 flex items-center justify-between border border-blue-100">
                    <div className="flex items-center space-x-3 overflow-hidden">
                        <File className="h-8 w-8 text-blue-500 flex-shrink-0" />
                        <div className="min-w-0">
                            <p className="text-sm font-medium text-slate-900 truncate">
                                {file.name}
                            </p>
                            <p className="text-xs text-slate-500">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={() => setFile(null)}
                        className="p-2 text-slate-400 hover:text-red-500 rounded-full hover:bg-white transition-colors"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>
            )}

            {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm border border-red-100">
                    {error}
                </div>
            )}

            <div className="mt-6 flex justify-end">
                <button
                    onClick={handleUpload}
                    disabled={!file || !supplierName.trim() || uploading}
                    className={`flex items-center px-6 py-2.5 rounded-lg font-medium text-white shadow-sm transition-all
            ${(!file || !supplierName.trim() || uploading)
                            ? 'bg-slate-300 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'}`}
                >
                    {uploading ? (
                        <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Загрузка...
                        </span>
                    ) : (
                        <>
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Загрузить и сопоставить
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
