/**
 * Export Service
 *
 * Handles exporting diagrams to various formats (SVG, PNG, PDF).
 * Uses html2canvas for PNG conversion and jsPDF for PDF generation.
 */

import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export type ExportFormat = 'svg' | 'png' | 'pdf';

export interface ExportOptions {
  format: ExportFormat;
  filename?: string;
  scale?: number; // For PNG quality (default: 2)
  backgroundColor?: string; // For PNG/PDF (default: white)
}

/**
 * Export diagram to specified format
 */
export async function exportDiagram(
  svgElement: HTMLElement,
  options: ExportOptions
): Promise<void> {
  const {
    format,
    filename = `diagram_${Date.now()}`,
    scale = 2,
    backgroundColor = '#ffffff',
  } = options;

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

/**
 * Export as SVG (native format)
 */
function exportAsSVG(svgElement: HTMLElement, filename: string): void {
  const svgData = svgElement.innerHTML;
  const blob = new Blob([svgData], { type: 'image/svg+xml' });
  downloadBlob(blob, `${filename}.svg`);
}

/**
 * Export as PNG using html2canvas
 */
async function exportAsPNG(
  svgElement: HTMLElement,
  filename: string,
  scale: number,
  backgroundColor: string
): Promise<void> {
  try {
    const canvas = await html2canvas(svgElement, {
      scale,
      backgroundColor,
      logging: false,
      useCORS: true,
    });

    // Wrap toBlob in Promise to properly handle errors
    const blob = await new Promise<Blob | null>((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to create PNG blob'));
        }
      }, 'image/png');
    });

    if (blob) {
      downloadBlob(blob, `${filename}.png`);
    } else {
      throw new Error('Failed to create PNG blob');
    }
  } catch (error) {
    console.error('PNG export failed:', error);
    throw new Error('Failed to export as PNG');
  }
}

/**
 * Export as PDF using jsPDF
 */
async function exportAsPDF(
  svgElement: HTMLElement,
  filename: string,
  backgroundColor: string
): Promise<void> {
  try {
    // First convert to canvas
    const canvas = await html2canvas(svgElement, {
      scale: 2,
      backgroundColor,
      logging: false,
      useCORS: true,
    });

    const imgData = canvas.toDataURL('image/png');
    const imgWidth = canvas.width;
    const imgHeight = canvas.height;

    // Calculate PDF dimensions (A4 in portrait or landscape based on aspect ratio)
    const aspectRatio = imgWidth / imgHeight;
    let pdfWidth: number;
    let pdfHeight: number;

    if (aspectRatio > 1) {
      // Landscape
      pdfWidth = 297; // A4 landscape width in mm
      pdfHeight = pdfWidth / aspectRatio;
    } else {
      // Portrait
      pdfHeight = 297; // A4 portrait height in mm
      pdfWidth = pdfHeight * aspectRatio;
    }

    const pdf = new jsPDF({
      orientation: aspectRatio > 1 ? 'landscape' : 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    // Center the image on the page
    const pageWidth = aspectRatio > 1 ? 297 : 210;
    const pageHeight = aspectRatio > 1 ? 210 : 297;
    const xOffset = (pageWidth - pdfWidth) / 2;
    const yOffset = (pageHeight - pdfHeight) / 2;

    pdf.addImage(imgData, 'PNG', xOffset, yOffset, pdfWidth, pdfHeight);
    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('PDF export failed:', error);
    throw new Error('Failed to export as PDF');
  }
}

/**
 * Helper to download blob as file
 */
function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Get SVG element from container
 */
export function getSVGElement(container: HTMLElement): HTMLElement | null {
  const svg = container.querySelector('svg');
  if (!svg) {
    return null;
  }
  // Return the SVG element itself or its parent div
  return (svg.parentElement as HTMLElement) || (svg as any as HTMLElement);
}
