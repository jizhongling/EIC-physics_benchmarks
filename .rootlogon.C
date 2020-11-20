{
  // Ensure fmt is loaded
  R__LOAD_LIBRARY(libfmt);

  // setup a local build directory so we don't polute our source code with
  // ROOT dictionaries etc.
  gSystem->SetBuildDir("/tmp/root_build");

  // style definition based off the ATLAS style
  TStyle* s = gStyle;

  // use plain black on white colors
  Int_t icol = 0; // WHITE
  s->SetFrameBorderMode(icol);
  s->SetFrameFillColor(icol);
  s->SetCanvasBorderMode(icol);
  s->SetCanvasColor(icol);
  s->SetPadBorderMode(icol);
  s->SetPadColor(icol);
  s->SetStatColor(icol);
  // s->SetFillColor(icol); // don't use: white fill color flor *all*
  // objects

  // set the paper & margin sizes
  s->SetPaperSize(TStyle::kUSLetter);
  s->SetPaperSize(20, 26);

  // set margin sizes
  s->SetPadTopMargin(0.05);
  s->SetPadRightMargin(0.05);
  s->SetPadBottomMargin(0.15);
  s->SetPadLeftMargin(0.12);

  // set title offsets (for axis label)
  s->SetTitleXOffset(1.3);
  s->SetTitleYOffset(1.1);

  // use large fonts
  // Int_t font=72; // Helvetica italics
  Int_t font = 43; // Helvetica
  Double_t tsize = 26;
  s->SetTextFont(font);

  s->SetTextSize(tsize);
  s->SetLabelFont(font, "x");
  s->SetTitleFont(font, "x");
  s->SetLabelFont(font, "y");
  s->SetTitleFont(font, "y");
  s->SetLabelFont(font, "z");
  s->SetTitleFont(font, "z");

  s->SetLabelSize(tsize, "x");
  s->SetTitleSize(tsize, "x");
  s->SetLabelSize(tsize, "y");
  s->SetTitleSize(tsize, "y");
  s->SetLabelSize(tsize, "z");
  s->SetTitleSize(tsize, "z");

  // use bold lines and markers
  s->SetMarkerStyle(20);
  s->SetMarkerSize(1.2);
  s->SetHistLineWidth(2.);
  s->SetLineStyleString(2, "[12 12]"); // postscript dashes

  // get rid of X error bars and y error bar caps
  // s->SetErrorX(0.001);

  // do not display any of the standard histogram decorations
  s->SetOptTitle(0);
  // s->SetOptStat(1111);
  s->SetOptStat(0);
  // s->SetOptFit(1111);
  s->SetOptFit(0);

  // put tick marks on top and RHS of plots
  s->SetPadTickX(1);
  s->SetPadTickY(1);

  // lower amount of y-ticks
  s->SetNdivisions(505, "Y");
}
