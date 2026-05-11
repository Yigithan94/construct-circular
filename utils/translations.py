"""
Translation utilities for criteria, subcriteria, and KPI content
"""

# Criteria translations (Turkish to English)
CRITERIA_TRANSLATIONS = {
    "Fonksiyonel Döngüsellik": "Functional Circularity",
    "Ürün Döngüselliği": "Product Circularity", 
    "Bileşen Döngüselliği": "Component Circularity",
    "Materyal Döngüselliği": "Material Circularity",
    "Enerji Döngüselliği": "Energy Circularity",
    "Referans Döngüsellik": "Reference Circularity"
}

# Criteria descriptions (Turkish to English)
CRITERIA_DESCRIPTIONS = {
    "DE Raporunda 7 toplumsal ihtiyaçlar ve istekler belirlenmiştir. DE fonksiyonlarını bu kapsamda barınma, hizmet, beslenme, sağlık hizmetleri, hareketlilik, iletişim, sarf malzemeler olarak sıralanmaktadır. Düşük gelirli ülkeler başta olmak üzere konut inşaatı ve onarımı en büyük kaynak ve emisyon payını oluşturmaktadır. Döngüsel Ekonomi kaynağın sadece kendi fonksiyonlarına bağlı kalması değil aynı zamanda diğer fonksiyonlara da hizmet ederek Döngüsellik oranının arttırılmasıyla da sağlanabilir.": "The CE Report identifies 7 societal needs and demands. CE functions are listed in this context as housing, services, nutrition, health services, mobility, communication, and consumables. Housing construction and renovation, especially in low-income countries, constitute the largest share of resources and emissions. Circular Economy can be achieved not only by the resource being tied to its own functions but also by serving other functions and increasing the Circularity rate.",
    
    "İnşaat endüstirisinin ürünü inşaat projelerinin sonucunda ortaya çıkan yapılardır. Diğer sektörlerle karşılaştırıldığında ürün (yani yapı) kullanım süresi en uzun sektörlerden birisidir. Diğer bir deyişle kaynağın ürün içerisinde uzun süre gömülü kaldığı bir üretim sektörüdür. Bu açıdan ürün bazında döngüselliği, halihazırda var olan projelerin döngüseliği ve yapılacak projeler için döngüselliğe elverişlilik olarak ikiye ayrıldığı söylenilebilir.": "The product of the construction industry is the structures that emerge as a result of construction projects. Compared to other sectors, it is one of the sectors with the longest product (i.e., structure) usage time. In other words, it is a production sector where resources remain embedded in the product for a long time. From this perspective, product-based circularity can be divided into two: the circularity of existing projects and the suitability for circularity of projects to be built.",
    
    "Yapı bileşenleri denilince akla çoğunlukla taşıyıcı sistemler gelmektedir. Geleneksel inşaatlarda betonarme kolonlar ve çelik donatılardan oluşan bu bu bileşenler modern inşaat yöntemleriyle ve genişleyen malzeme yelpazesiyle birlikte yapı kullanımı amacına göre çeşitli bileşenler ortaya çıkmaktadır. Dış cephe bileşenleri, ısı yalıtım bileşenleri, havalandırma DE bileşenlerini oluşturanlardan birkaçıdır.": "In the context of construction, structural elements such as reinforced concrete columns and steel reinforcements are often considered the primary components. However, with the advancement of modern construction methods and the expansion of material options, various building components are now designed according to the functional requirements of the structure. These may include façade systems, insulation layers, and ventilation elements. Component circularity refers to the ability of these elements to be reused, disassembled, or recycled, and plays a critical role in enhancing the overall circular performance of the built environment.",
    
    "DE ilk adımını malzemelerin seçilmesiyle başlanıldığı söylenebilir. Ancak ürün oluşturulurken malzemeler sürdürülebilirlik ölçütlerinden ziyade kar odaklı seçilebilmektedir. Bu açıdan inşaat endüstrisinde malzemelerin dönüşüm katkısı için arz talep dengesinin oluşması önemlidir. Özellikle DE'nin en çok kullanılan yöntemlerinden birisi olan geri dönüşüm, her zaman çevreci olmayabilir. Atık malzemenin kalitesi düşükse, geri dönüşüm işlemi çevresel etkiler açısından enerji geri kazanımından daha olumsuz olabilmektedir.": "Material selection represents the initial and most critical stage in achieving circularity within construction projects. However, in practice, material choices are often guided by cost-efficiency and short-term profitability rather than environmental sustainability. This discrepancy undermines the principles of material circularity, which aims to retain materials at their highest utility and value across multiple life cycles. A well-functioning supply-demand equilibrium is essential to support the systemic adoption of circular materials in the built environment. Notably, recycling—while frequently promoted as a circular solution—does not always guarantee environmental benefits. In cases where the quality of waste materials is poor, recycling processes may generate higher environmental impacts than alternative strategies such as energy recovery. Therefore, the environmental performance of recycling must be critically assessed within the broader material circularity framework.",
    
    "Malzemenin ve ürünün üretim enerjisi, lojistik enerji, inşaat için harcanan enerjinin yanısıra tesis yönetimi boyunca harcanan enerjiyi ve hatta yıkım yani dönüşüm için harcanan enerji süreclerini kapsar. Kaynaktan tasarruf sağlamak ve kaynağı verimli kullanmak için enerjinin doğru kaynaktan ve doğru miktarda tüketilmesi gerekmektedir. Bu açıdan malzemelerin gömülü enerji hesabı yapılmış olması döngüsel ekonomi açısından kıyaslanabilirlik oluşturmaktadır.": "This indicator encompasses the total energy consumed across the entire life cycle of a material or product — including energy used in production, logistics, construction, facility operation, and even end-of-life processes such as demolition and recovery. In a circular economy framework, energy should be sourced appropriately and used efficiently to ensure resource conservation. In this regard, accounting for the embodied energy of materials provides a meaningful basis for comparing their circularity performance and supports informed material selection.",
    
    "Lineer ekonomi yani \"al-yap-kullan-at\" modeliyle üretilen ürünlerin bir referans noktası oluşturarak döngüsellik açısından kıyaslanabilirlik sağlayacağı düşünülmektedir. Bu kriterlerin sağladıklar DE ölçümlenirken referanslarıyla karşılaştırılması daha uygun görülmüştür. Karşılaştırma yapılırken yüklenici seçimi için temel öneme sahip kriterlere Döngüsellik açısından yapılan katkısı önem arz etmektedir. Örneğin DE faydalı ancak dolaylı etkilerle Teknik bir problem yaratarak döngüselliğe zarar verebilme olasılığına sahipse bu ürün DE etkin ürün olmaktan çıkabilir. Bu açıdan referanslarına göre Döngüsellik kavramı önemli olabilmektedir.": "It is thought that products produced with the linear economy, i.e., the \"take-make-use-dispose\" model, will provide comparability in terms of circularity by creating a reference point. It was deemed more appropriate to compare what these criteria provide with their references when measuring CE. When making comparisons, the contribution made in terms of Circularity to criteria that are of fundamental importance for contractor selection is important. For example, if CE is beneficial but has the potential to harm circularity by creating a technical problem through indirect effects, this product may cease to be a CE-effective product. In this regard, the concept of Circularity according to its references may be important."
}

# Sub-criteria translations (first 15 entries)
SUBCRITERIA_TRANSLATIONS = {
    "Organizasyon yapısı": "Organizational Structure",
    "Sosyal ilerleme": "Social Progress", 
    "Entegre Proje Teslimati (IPD) ve İnşaat Yönetimi (CM) tedarik türleri deneyimi": "Integrated Project Delivery (IPD) and Construction Management (CM) Procurement Experience",
    "Şantiye sahasında döngüsellik": "On-site Circularity",
    "Yeşil tedarik": "Green Procurement",
    "Tedarik zinciri döngüselliği": "Supply Chain Circularity",
    "Taşıma öncesi ürün hata kontrolü": "Pre-transport Product Quality Control",
    "Hizmet olarak ürün modelleri": "Product-as-a-Service Models",
    "Bileşenlerin farklı projelerde kullanılabilirliği": "Component Reusability Across Projects",
    "Bileşen seçimi, koruması ve bakımı yoluyla bina yapısının dayanıklılığının arttırılması": "Enhancing Building Structure Durability through Component Selection, Protection and Maintenance",
    "Modüler elemanların önceliklendirilmesi": "Prioritization of Modular Elements",
    "Farklı katmanlardaki bileşenler arasında tersine çevrilebilir bağlantıların kullanılması": "Use of Reversible Connections Between Components at Different Layers",
    "Yapı için bir söküm kılavuzu": "Disassembly Guide for Structures",
    "Kaynak tüketimi ve entegre kullanım oranı": "Resource Consumption and Integrated Utilization Rate",
    "Malzeme israfının azaltılması ve yalın üretim zinciri": "Reduction of material waste and the lean production chain",
    "Geri dönüştürülmüş hammaddelerin kullanımı": "Utilization of recycled raw materials",
    "Projeye ait Yapı Malzemeleri Pasaport belgesi": "Building Materials Passport document for the project",
    "Malzeme Listesi (BoL) aracılığıyla malzeme toksikolojisinin değerlendirilmesi": "Assess material toxicology through the BoL and mitigate monstrous hybrids."
}

# Sub-criteria descriptions (Turkish to English)
SUBCRITERIA_DESCRIPTIONS = {
    "İşveren deneyimi göz önünde bulundurulursa yüklenicilerin bileşen döngüselliğini değerlendirmek için organizasyon yapısını bilmesi önemlidir.": "Considering the employer's experience, it is important for contractors to know the organizational structure to evaluate component circularity.",
    
    "Bileşen döngüselliği çalışanların sosyal refahını arttırmaktadır. İşverenlerin sosyal gelişimleri göz önüne alındığında yüklenicilerin sosyal gelişimlerine yaptığı katkı performans ölçütlerinden birisidir.": "Component circularity increases the social welfare of employees. Considering the social development of employers, the contribution of contractors to social development is one of the performance criteria.",
    
    "İşverenlerin, Döngüsel Ekonomi için IPD ve CM gibi satın alma türlerine aşinalığı olması tercih edilir. Yükleniciler söz konusu olduğunda, önceki projelerdeki bu tür tedarik deneyimi çok önemlidir.": "It is preferred that employers are familiar with procurement types such as IPD and CM for Circular Economy. When it comes to contractors, such procurement experience in previous projects is crucial.",
    
    "Şantiye sahasında malzemenin verimli kullanımı, kıt kaynakların tasarruflu kullanımı, yeniden kullanım, geri kazanım vb döngüselliği artırmaktadır.": "Efficient use of materials on the construction site, economical use of scarce resources, reuse, recovery, etc. increase circularity.",
    
    "Bileşen döngüselliği sürecinde bir ürün ya da bileşenin tedarik sürecinde döngüsellik kurallarının uygulanması döngüselliği arttırmaktadır.": "Applying circularity rules in the procurement process of a product or component during the component circularity process increases circularity.",
    
    "Tedarik zincirinde döngüsellik kurallarının uygulanması genel döngüselliği arttırmaktadır.": "Applying circularity rules in the supply chain increases overall circularity.",
    
    "Ürün ya da bileşenin taşıma öncesinde muayenesi döngüselliğe olumlu katkı sunmaktadır.": "Inspection of the product or component before transport makes a positive contribution to circularity.",
    
    "Satın alma yerine kiralama modeli döngüsellik etkinliğini arttırmaktadır.": "The rental model instead of purchasing increases circularity effectiveness.",
    
    "Bir bileşenin farklı projelerde kullanılabilir olması döngüsellik açısından önem arz etmektedir.": "The reusability of a component in different projects is important for circularity.",
    
    "Bileşen seçimi, bakımı ve koruması döngüselliğe olumlu katkı sunmaktadır.": "Component selection, maintenance and protection make a positive contribution to circularity.",
    
    "Modüler sistemlerin kullanımı sökülebilirlik açısından döngüselliğe olumlu katkı sunmaktadır.": "The use of modular systems makes a positive contribution to circularity in terms of disassembly.",
    
    "Farklı katmanlardaki bileşenler arasında tersine çevrilebilir bağlantıların kullanımı döngüselliği olumlu yönde desteklemektedir.": "The use of reversible connections between components at different layers positively supports circularity.",
    
    "Yapı için bir söküm kılavuzu hazırlanması döngüselliğe olumlu katkı sunmaktadır.": "Preparing a disassembly guide for the structure makes a positive contribution to circularity.",
    
    "Kaynak tüketimi ve entegre kullanım oranı kaynağın verimli kullanımı açısından döngüsellik performansını ölçmektedir.": "This indicator assesses not only the consumption rates of various resource types within a project—such as minerals and energy—but also evaluates how efficiently and collectively these resources are utilized. In addition to calculating resource use per unit of GDP, it emphasizes the importance of integrated resource management by considering synergies and co-usage efficiency across different resource streams.",
    
    "Bir projenin farklı kaynak türlerinin tüketim oranını belirlerken aynı zamanda bu kaynakların bir arada nasıl kullanıldığını göz önünde bulundurur. Mineral ve enerji tüketimlerini hesaplanarak birim GDP olarak ifade edilmesine ek olarak, kaynakların birleşik ve verimli kullanımını da değerlendirir.": "This indicator assesses not only the consumption rates of various resource types within a project—such as minerals and energy—but also evaluates how efficiently and collectively these resources are utilized. In addition to calculating resource use per unit of GDP, it emphasizes the importance of integrated resource management by considering synergies and co-usage efficiency across different resource streams.",
    
    "Malzeme israfının azaltılması ve yalın üretim zinciri döngüsellik açısından önem arz etmektedir.": "Material waste reduction and lean production chain are important for circularity.",
    
    "Diğer biobazlı malzemelerin yanı sıra işlenmiş ahşap ve geri dönüştürülmüş içerikli betonun kullanılması projelerde döngüselliği artırır.": "The use of processed wood and concrete with recycled content, along with other bio-based materials, increases circularity in projects.",
    
    "Döngüsel inşaat için kaynak kullanımını izlemek, değerlendirmek ve optimize edilmelidir. Yapı bileşenlerinin ve malzemelerinin başarılı bir şekilde geri kazanılması ve daha sonra kullanılması için bilinçli ve kolayca erişilebilen ayrıntılı bilgiler vazgeçilmezdir.": "For circular construction, resource use must be monitored, evaluated, and optimized. Conscious and easily accessible detailed information is indispensable for the successful recovery and subsequent use of building components and materials.",
    
    "BoL aracılığıyla malzeme toksikolojisinin belirlenmesi, daha çevre dostu ve daha sağlıklı malzemelerin tercih edilmesini kolaylaştırmaktadır. Bu, daha güvenli, çevre dostu ve sürdürülebilir ürünlerin benimsenmesini kolaylaştırarak zararlı malzemelerin kullanımını önleyerek CE'ye katkıda bulunur.": "Determining material toxicology through the BoL facilitates the preference for more environmentally friendly and healthier materials. This contributes to CE by preventing the use of harmful materials and facilitating the adoption of safer, more environmentally friendly and sustainable products."
}

def get_translated_criterion_name(turkish_name, locale='en'):
    """Get translated criterion name based on locale"""
    if locale == 'en':
        return CRITERIA_TRANSLATIONS.get(turkish_name, turkish_name)
    return turkish_name

def get_translated_criterion_description(turkish_description, locale='en'):
    """Get translated criterion description based on locale"""
    if locale == 'en':
        # Strip whitespace from description for dictionary lookup
        cleaned_description = turkish_description.strip() if turkish_description else turkish_description
        return CRITERIA_DESCRIPTIONS.get(cleaned_description, turkish_description)
    return turkish_description

def get_translated_subcriterion_name(turkish_name, locale='en'):
    """Get translated sub-criterion name based on locale"""
    if locale == 'en':
        return SUBCRITERIA_TRANSLATIONS.get(turkish_name, turkish_name)
    return turkish_name

def get_translated_subcriterion_description(turkish_description, locale='en'):
    """Get translated sub-criterion description based on locale"""
    if locale == 'en':
        # Strip whitespace from description for dictionary lookup
        cleaned_description = turkish_description.strip() if turkish_description else turkish_description
        return SUBCRITERIA_DESCRIPTIONS.get(cleaned_description, turkish_description)
    return turkish_description