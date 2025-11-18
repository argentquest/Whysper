```typescript
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export type ExportFormat = 'svg' | 'png' | 'pdf';

export interface ExportOptions {
  format: ExportFormat;
  filename?: string;
  scale?: number; // For PNG quality (default: 2)
  backgroundColor?: string; // For PNG/PDF (default: white)
}

export async function exportDiagram(
  svgElement: HTMLElement,
  options: ExportOptions
): Promise<void> {
  // Destructure options with default values for flexible configuration
  const {
    format,
    filename = `diagram_${Date.now()}`, // Generate unique filename if not provided
    scale = 2,
    backgroundColor = '#ffffff',
  } = options;

  // Route export based on selected format using switch statement for clear control flow
  switch (format) {
    case 'svg':
      return exportAsSVG(svgElement, filename);
    case 'png':
      return exportAsPNG(svgElement, filename, scale, backgroundColor);
    case 'pdf':
      return exportAsPDF(svgElement, filename, backgroundColor);
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

function exportAsSVG(svgElement: HTMLElement, filename: string): void {
  // Convert SVG content directly to blob for simple SVG download
  const svgData = svgElement.innerHTML;
  const blob = new Blob([svgData], { type: 'image/svg+xml' });
  downloadBlob(blob, `${filename}.svg`);
}

async function exportAsPNG(
  svgElement: HTMLElement,
  filename: string,
  scale: number,
  backgroundColor: string
): Promise<void> {
  try {
    // Use html2canvas to render SVG to high-quality canvas with specified settings
    const canvas = await html2canvas(svgElement, {
      scale,
      backgroundColor,
      logging: false,
      useCORS: true,
    });

    // Wrap toBlob in Promise to handle asynchronous blob creation safely
    const blob = await new Promise<Blob | null>((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to create PNG blob'));
        }
      }, 'image/png');
    });

    // Download blob if successfully created, otherwise throw error
    if (blob) {
      downloadBlob(blob, `${filename}.png`);
    } else {
      throw new Error('Failed to create PNG blob');
    }
  } catch (error) {
    // Log and rethrow errors for comprehensive error handling
    console.error('PNG export failed:', error);
    throw new Error('Failed to export as PNG');
  }
}

async function exportAsPDF(
  svgElement: HTMLElement,
  filename: string,
  backgroundColor: string
): Promise<void> {
  try {
    // Convert SVG to canvas first for precise PDF rendering
    const canvas = await html2canvas(svgElement, {
      scale: 2,
      backgroundColor,
      logging: false,
      useCORS: true,
    });

    const imgData = canvas.toDataURL('image/png');
    const imgWidth = canvas.width;
    const imgHeight = canvas.height;

    // Dynamically determine PDF orientation based on image aspect ratio
    const aspectRatio = imgWidth / imgHeight;
    let pdfWidth: number;
    let pdfHeight: number;

    // Calculate PDF dimensions to maintain original aspect ratio
    if (aspectRatio > 1) {
      // Landscape orientation calculation
      pdfWidth = 297; // A4 landscape width in mm
      pdfHeight = pdfWidth / aspectRatio;
    } else {
      // Portrait orientation calculation
      pdfHeight = 297; // A4 portrait height in mm
      pdfWidth = pdfHeight * aspectRatio;
    }

    // Create PDF with dynamic orientation matching image
    const pdf = new jsPDF({
      orientation: aspectRatio > 1 ? 'landscape' : 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    // Center image on PDF page for professional layout
    const pageWidth = aspectRatio > 1 ? 297 : 210;
    const pageHeight = aspectRatio > 1 ? 210 : 297;
    const xOffset = (pageWidth - pdfWidth) / 2;
    const yOffset = (pageHeight - pdfHeight) / 2;

    // Add image to PDF and save with calculated positioning
    pdf.addImage(imgData, 'PNG', xOffset, yOffset, pdfWidth, pdfHeight);
    pdf.save(`${filename}.pdf`);
  } catch (error) {
    // Log and rethrow errors for comprehensive error handling
    console.error('PDF export failed:', error);
    throw new Error('Failed to export as PDF');
  }
}

function downloadBlob(blob: Blob, filename: string): void {
  // Create temporary link element to trigger file download programmatically
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function getSVGElement(container: HTMLElement): HTMLElement | null {
  // Find SVG element within container for export
  const svg = container.querySelector('svg');
  if (!svg) {
    return null;
  }
  // Return SVG or its parent element for flexible selection
  return (svg.parentElement as HTMLElement) || (svg as any as HTMLElement);
}