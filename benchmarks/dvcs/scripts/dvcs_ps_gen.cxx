void dvcs_ps_gen() {
  double E_p = 100.0;
  double M_p = 0.938;
  double E_e = 5.0;
   TLorentzVector target(0.0, 0.0, std::sqrt(E_p*E_p - M_p*M_p),E_p);
   TLorentzVector beam(0.0, 0.0, E_e, std::sqrt(E_e*E_e+0.000511*0.000511));
   TLorentzVector W = beam + target;

   //(Momentum, Energy units are Gev/C, GeV)
   Double_t masses[3] = { 0.000511,0.938, 0.0} ;

   TGenPhaseSpace event;
   if(!event.SetDecay(W, 3, masses))
     std::cout << "derp\n";
     ;

   TH2F *h2 = new TH2F("h2","h2; Q^{2} ; t", 100,0,5, 100,-0.120,0);

   for (Int_t n=0;n<1000000;n++) {
      Double_t weight = event.Generate();

      TLorentzVector* pElectron = event.GetDecay(0);
      TLorentzVector* pProton = event.GetDecay(1);
      TLorentzVector* pGamma = event.GetDecay(2);

      TLorentzVector pq = beam - *pElectron;
      TLorentzVector Delta = target - *pProton;

      h2->Fill(-1.0*(pq.M2()) , Delta.M2() ,weight);
      //std::cout <<  -1.0*(pq.M2())  << " , " <<  Delta.M2() << " , " << weight << "\n";
   }
   h2->Draw("colz");
}
